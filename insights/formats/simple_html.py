from insights.formats import FormatterAdapter
from insights.formats.html import HtmlFormat


class SimpleHtmlFormat(HtmlFormat):
    """
    This class prints a html summary of rule hits. It should be used
    as a context manager and given an instance of an
    ``insights.core.dr.Broker``. ``dr.run`` should be called within the context
    using the same broker.

    Args:
        broker (Broker): the broker to watch and provide a summary about.
        stream (file-like): Output is written to stream. Defaults to sys.stdout.
    """

    TEMPLATE = """
<!doctype html>
<html lang="en">
  <head>
    <!-- Required meta tags -->
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">

    <title>{{root}}</title>
    <style>
    a.pass {
      color: green;
    }
    a.fail {
      color: red;
    }
    a.source {
      color: orange;
    }
    .main {
      margin-top: 100px;
      margin-bottom: 100px;
      margin-right: 150px;
      margin-left: 80px;
    }
    </style>
  </head>
  <body>
  <div class="main">
  <h2 align="center">Analysis of {{root}}</h2>
  <h4 align="center">Performed at {{start_time}} UTC</h4>
    <section>
      <h2>System Information</h2>
        <pre>
        {%- for rule in rules.make_info %}
{{rule.body}}
        {%- endfor %}
        </pre>
    </section>
    <h2>Rule Results</h2>
    <nav>
      <ul>
        {%- for response_type, rule_group in rules.items() %}
        {%- if response_type != "make_info" %}
        {%- for rule in rule_group %}
        <ul>
          <a id="{{rule.id}}_top"
             class="{% if response_type !='make_pass' %}fail{% else %}pass{% endif %}"
             href="#{{rule.id}}">
          {{rule.name}}
          </a>
        </ul>
        {%- endfor %}
        {%- endif %}
        {%- endfor %}
      </ul>
    </nav>
    <section>
    <h2>Rule Result Details</h2>
        {%- for response_type, rule_group in rules.items() %}
        {%- if response_type != "make_info" %}
        {%- for rule in rule_group %}
        <article>
          <header>
          <a id="{{rule.id}}"
             class="{% if response_type !='make_pass' %}fail{% else %}pass{% endif %}"
             href="#{{rule.id}}_top">
          {{rule.name}}
          </a>
          </header>
          <p>
          <pre>
{{rule.body}}
          </pre>
          </p>

          <hr />
          <p>
Contributing Data:
          <ol>
          {%- for d in rule.datasources %}
          <li>{{d}}</li>
          {%- endfor %}
          </ol>
          </p>

          <hr />
          Links:
          <ul>
          {% for cat, links in rule.links.items() %}
            <li>{{cat}}
            <ul>
            {% for link in links %}
            <li><a class="source" href="{{link}}">{{link}}</a></li>
            {% endfor %}
            </ul>
            </li>
          {%- endfor %}
          </ul>

          <hr />
          <p> Rule Source: <a class="source" href="file://{{rule.source_path}}">{{rule.source_path}}</a></p>

          <hr />
          <div>
          <p>
          Documentation:
          <div>
          <pre>
{{rule.mod_doc}}
{{rule.rule_doc}}
          </pre>
          </div>
          </p>
          </div>
          <hr />
        </article>
        {%- endfor %}
        {%- endif %}
        {%- endfor %}
    </section>
  </div>
  </body>
</html>
    """.strip()


# this connects the formatter to the insights run CLI bits
class SimpleHtmlFormatterAdapter(FormatterAdapter):
    """ Displays results in a simple html format. """

    def preprocess(self, broker):
        self.formatter = SimpleHtmlFormat(broker)
        self.formatter.preprocess()

    def postprocess(self, broker):
        self.formatter.postprocess()
