<html>
<head>
    <meta charset="utf-8" />
</head>
<meta name="viewport" content="width=device-width, initial-scale=1.0, shrink-to-fit=no" />
<title>{{ username }} -- socialspot   </title>
<body>
    <div class="container">
        <div class="row-mb">
            <div class="col-12 card-body" style="padding-bottom: 0.5rem; width:100%">
                <h2 class="mb-0">
                    Username search report for {{ username }}
                </h2>
                <small>{{ generated_at }}</small>
            </div>
        </div>
        <br/><br/>
        <div>
                <div>
                    <div>
                        <div>
                            <h3>Supposed personal data</h3>
                            {% for k, v in supposed_data.items() %}
                            <p>
                                {{ k }}: {{ v }}
                            </p>
                            {% endfor %}
                            {% if countries_tuple_list %}
                          
                            {% endif %}{% if interests_tuple_list %}
                            <p>
                                Interests: {% for k, v in interests_tuple_list %}{{ k }} <span class="text-muted">({{ v }})</span>{{ ", " if not loop.last }}{% endfor %}
                            </p>
                            {% endif %}{% if first_seen %}
                            <p>
                                First seen: {{ first_seen }}
                            </p>
                            {% endif %}
                        </div>
                    </div>
                </div>
            </div>
            <br/>
            <div>
                <div>
                    <div>
                        <div>
                            <h3>Brief</h3>
                            <p>
                                {{ brief }}
                            </p>
                        </div>
                    </div>
                </div>
            </div>
            {% for u, t, data in results %}
                {% for k, v in data.items() %}
                    {% if v.found and not v.is_similar %}
            <split></split>
            <hr>
            <br/>
            <div class="sitebox" style="margin-top: 20px;" >
                <div>
                    <div>
                        <table>
                            <tr>
                                <td valign="top">
                                    <div class="textbox" style="padding-top: 10px;" >
                                        <h3>
                                            <a class="text-dark" href="{{ v.url_main }}" target="_blank">{{ k }}</a>
                                        </h3>
                                        {% if v.status.tags %}
                                            <div class="mb-1 text-muted">Tags: {{ v.status.tags | join(', ') }}</div>
                                        {% endif %}
                                        <p class="card-text">
                                            <a href="{{ v.url_user }}" target="_blank">{{ v.url_user }}</a>
                                        </p>
                                    </div>
                                    {% if v.ids_data %}
                                    <div style="clear:both;"></div>
                                    <div style="width:100%">
                                    <br/>
                                    <h4>Details</h4>
                                    <table class="table table-striped;" style="margin-top:5px;">
                                        <tbody>
                                        {% for k1, v1 in v.ids_data.items() %}
                                            {% if k1 != 'image' %}
                                            <tr>
                                                <th style="width:200px;">{{ title(k1) }}</th>
                                                <td>{% if v1 is iterable and (v1 is not string and v1 is not mapping) %}{{ v1 | join(', ') }}{% else %}{{ detect_link(v1) }}{% endif %}</td>
                                            </tr>
                                            {% endif %}

                                        {% endfor %}
                                        </tbody>
                                    </table>
                                    </div>
                                    {% endif %}
                                </td>
                                <td style="width:201px; position: relative;" valign="top">
                                    <img alt="Photo" style="width: 200px; height: 200px; object-fit: scale-down;" src="{{ v.status.ids_data.image or 'https://i.imgur.com/040fmbw.png' }}" data-holder-rendered="true">
                                </td>
                            </tr>
                        </table>
                    </div>
                </div>
            </div>
                    {% endif %}
                {% endfor %}
            {% endfor %}
    </div>
</body>
</html>