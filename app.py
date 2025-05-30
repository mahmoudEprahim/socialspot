import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))

if current_dir not in sys.path:
    sys.path.append(current_dir)

from flask import (
    Flask,
    render_template,
    request,
    send_file,
    Response,
    flash,
    redirect,
    url_for,
)
import logging
import asyncio
from datetime import datetime
from threading import Thread

import socialspot
import socialspot.settings
from socialspot.sites import socialspotDatabase
from socialspot.report import generate_report_context
import socialspot.result



template_folder_path = os.path.join(current_dir, 'socialspot', 'web', 'templates')
static_folder_path =os.path.join(current_dir, 'socialspot', 'web', 'static')
app = Flask(__name__, template_folder=template_folder_path ,static_folder=static_folder_path )
app.secret_key = 'your-secret-key-here'

background_jobs = {}
job_results = {}

socialspot_DB_FILE = os.path.join('socialspot', 'resources', 'data.json')

REPORTS_FOLDER = os.path.join(current_dir, 'reports_output')

os.makedirs(REPORTS_FOLDER, exist_ok=True)


def setup_logger(log_level, name):
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    return logger


async def socialspot_search(username, options):
    logger = setup_logger(logging.WARNING, 'socialspot')
    try:
        db = socialspotDatabase().load_from_path(socialspot_DB_FILE)

        top_sites = int(options.get('top_sites') or 500)
        if options.get('all_sites'):
            top_sites = 999999999

        tags = options.get('tags', [])
        site_list = options.get('site_list', [])
        logger.info(f"Filtering sites by tags: {tags}")

        sites = db.ranked_sites_dict(
            top=top_sites,
            tags=tags,
            names=site_list,
            disabled=False,
            id_type='username'
        )

        logger.info(f"Found {len(sites)} sites matching the tag criteria")

        results = await socialspot.search(
            username=username,
            site_dict=sites,
            timeout=int(options.get('timeout', 30)),
            logger=logger,
            id_type='username',
            is_parsing_enabled=(not options.get('disable_extracting', False)),
            recursive_search_enabled=(not options.get('disable_recursive_search', False)),
            check_domains=options.get('with_domains', False),
            proxy=options.get('proxy', None),
            tor_proxy=options.get('tor_proxy', None),
            i2p_proxy=options.get('i2p_proxy', None),
        )
        return results
    except Exception as e:
        logger.error(f"Error during search: {str(e)}")
        raise


async def search_multiple_usernames(usernames, options):
    results = []
    for username in usernames:
        try:
            search_results = await socialspot_search(username.strip(), options)
            results.append((username.strip(), 'username', search_results))
        except Exception as e:
            logging.error(f"Error searching username {username}: {str(e)}")
    return results


def process_search_task(usernames, options, timestamp):
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        general_results = loop.run_until_complete(
            search_multiple_usernames(usernames, options)
        )

        session_folder = os.path.join(REPORTS_FOLDER, f"search_{timestamp}")
        os.makedirs(session_folder, exist_ok=True)

        graph_path = os.path.join(session_folder, "combined_graph.html")
        socialspot.report.save_graph_report(
            graph_path,
            general_results,
            socialspotDatabase().load_from_path(socialspot_DB_FILE),
        )

        individual_reports = []
        for username, id_type, results in general_results:
            report_base = os.path.join(session_folder, f"report_{username}")

            csv_path = f"{report_base}.csv"
            json_path = f"{report_base}.json"
            pdf_path = f"{report_base}.pdf"
            html_path = f"{report_base}.html"

            context = generate_report_context(general_results)

            socialspot.report.save_csv_report(csv_path, username, results)
            socialspot.report.save_json_report(
                json_path, username, results, report_type='ndjson'
            )
            socialspot.report.save_pdf_report(pdf_path, context)
            socialspot.report.save_html_report(html_path, context)

            claimed_profiles = []
            for site_name, site_data in results.items():
                if (
                    site_data.get('status')
                    and site_data['status'].status
                    == socialspot.result.socialspotCheckStatus.CLAIMED
                ):
                    claimed_profiles.append(
                        {
                            'site_name': site_name,
                            'url': site_data.get('url_user', ''),
                            'tags': (
                                site_data.get('status').tags
                                if site_data.get('status')
                                else []
                            ),
                        }
                    )

            individual_reports.append(
                {
                    'username': username,
                    'csv_file': os.path.join(
                        f"search_{timestamp}", f"report_{username}.csv"
                    ),
                    'json_file': os.path.join(
                        f"search_{timestamp}", f"report_{username}.json"
                    ),
                    'pdf_file': os.path.join(
                        f"search_{timestamp}", f"report_{username}.pdf"
                    ),
                    'html_file': os.path.join(
                        f"search_{timestamp}", f"report_{username}.html"
                    ),
                    'claimed_profiles': claimed_profiles,
                }
            )

        job_results[timestamp] = {
            'status': 'completed',
            'session_folder': f"search_{timestamp}",
            'graph_file': os.path.join(f"search_{timestamp}", "combined_graph.html"),
            'usernames': usernames,
            'individual_reports': individual_reports,
        }

    except Exception as e:
        logging.error(f"Error in search task for timestamp {timestamp}: {str(e)}")
        job_results[timestamp] = {'status': 'failed', 'error': str(e)}
    finally:
        background_jobs[timestamp]['completed'] = True

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def search_page():
    db = socialspotDatabase().load_from_path(socialspot_DB_FILE)
    site_options = []

    for site in db.sites:
        site_options.append(site.name)
        if site.url_main and site.url_main not in site_options:
            site_options.append(site.url_main)

    site_options = sorted(set(site_options))

    return render_template('search.html', site_options=site_options)
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/search', methods=['POST'])
def search():
    usernames_input = request.form.get('usernames', '').strip()
    if not usernames_input:
        flash('At least one username is required', 'danger')
        return redirect(url_for('index'))

    usernames = [
        u.strip() for u in usernames_input.replace(',', ' ').split() if u.strip()
    ]

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    selected_tags = request.form.getlist('tags')
    logging.info(f"Selected tags: {selected_tags}")

    options = {
        'top_sites': request.form.get('top_sites') or '500',
        'timeout': request.form.get('timeout') or '90',
        'all_sites': 'all_sites' in request.form,
        'site_list': [s.strip() for s in request.form.get('site', '').split(',') if s.strip()],
    }
    logging.info(f"DEBUG: Final options sent to socialspot: {options}")
    logging.info(f"Starting search for usernames: {usernames} with tags: {selected_tags}")

    background_jobs[timestamp] = {
        'completed': False,
        'thread': Thread(
            target=process_search_task, args=(usernames, options, timestamp)
        ),
    }
    background_jobs[timestamp]['thread'].start()

    return redirect(url_for('status', timestamp=timestamp))

@app.route('/status/<timestamp>')
def status(timestamp):
    logging.info(f"Status check for timestamp: {timestamp}")

    if timestamp not in background_jobs:
        flash('Invalid search session.', 'danger')
        logging.error(f"Invalid search session: {timestamp}")
        return redirect(url_for('index'))

    if background_jobs[timestamp]['completed']:
        result = job_results.get(timestamp)
        if not result:
            flash('No results found for this search session.', 'warning')
            logging.error(f"No results found for completed session: {timestamp}")
            return redirect(url_for('index'))

        if result['status'] == 'completed':
            return redirect(url_for('results', session_id=result['session_folder']))
        else:
            error_msg = result.get('error', 'Unknown error occurred.')
            flash(f'Search failed: {error_msg}', 'danger')
            logging.error(f"Search failed for session {timestamp}: {error_msg}")
            return redirect(url_for('index'))

    return render_template('status.html', timestamp=timestamp)


@app.route('/results/<session_id>')
def results(session_id):
    result_data = next(
        (
            r
            for r in job_results.values()
            if r.get('status') == 'completed' and r['session_folder'] == session_id
        ),
        None,
    )

    if not result_data:
        flash('No results found for this session ID.', 'danger')
        logging.error(f"Results for session {session_id} not found in job_results.")
        return redirect(url_for('index'))

    return render_template(
        'results.html',
        usernames=result_data['usernames'],
        graph_file=result_data['graph_file'],
        individual_reports=result_data['individual_reports'],
        timestamp=session_id.replace('search_', ''),
    )


@app.route('/reports/<path:filename>')
def download_report(filename):
    try:
        file_path = os.path.normpath(os.path.join(REPORTS_FOLDER, filename))
        if not file_path.startswith(REPORTS_FOLDER):
            raise Exception("Invalid file path attempted")
        return send_file(file_path)
    except Exception as e:
        logging.error(f"Error serving file {filename}: {str(e)}")
        return "File not found", 404


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )
    logging.getLogger('socialspot.search').setLevel(logging.DEBUG)
    logging.getLogger('socialspot.site').setLevel(logging.DEBUG)

    debug_mode = os.getenv('FLASK_DEBUG', 'true').lower() in ['true', '1', 't']
    app.run(debug=debug_mode)