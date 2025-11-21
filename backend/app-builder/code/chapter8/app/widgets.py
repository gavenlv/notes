from flask_appbuilder.widgets import RenderTemplateWidget

class ContactCardWidget(RenderTemplateWidget):
    template = 'widgets/contact_card.html'

class StatsChartWidget(RenderTemplateWidget):
    template = 'widgets/stats_chart.html'
    
    def __init__(self, chart_title='', labels=None, values=None):
        self.chart_title = chart_title
        self.labels = labels or []
        self.values = values or []