from django.views.generic import TemplateView
from data.models import DataFrame
from django.http import HttpResponse
import json
import sys
from pprint import pprint
from django.utils import timezone
import datetime


# Move this later 		
class CustomJSONEncoder(json.JSONEncoder):
	def default(self, obj):
		if hasattr(obj, 'isoformat'): #handles both date and datetime objects
			return obj.isoformat()
 		elif hasattr(obj, 'total_seconds'):
 			return str(obj)
		else:
			return json.JSONEncoder.default(self, obj)


class ChartBuilderView(TemplateView):
	template_name = "chart_builder.html"

	def get(self, request, *args, **kwargs):
		context = super(ChartBuilderView, self).get_context_data(**kwargs)
		column_names = request.GET.getlist("column_names[]");
		row_names = request.GET.getlist("row_names[]");

		try:
			dataframe = DataFrame.objects.get(pk = request.GET.get('dataframe_id'))
		except Exception,e:
			context['debug'] = str(e)
			return self.render_to_response(context)
			
		context['dataframe'] = dataframe

		return self.render_to_response(context)

def chart_selector(dataframe, chart_builder_input):
	ncols = len(chart_builder_input["column_names"])
	nrows = len(chart_builder_input["row_names"])
	
	if ncols + nrows == 1:
		return "pieChart"  
	elif (ncols == 1) and (nrows == 1):
		return "lineChart"  
	else:
		return "none"



class AutoChartView(TemplateView):
	template_name = "autochart.html"

	def get(self, request, *args, **kwargs):
		context = super(AutoChartView, self).get_context_data(**kwargs)

		chart_builder_input = json.loads(request.GET.get("chart_builder_input"))
		
		dataframe_id = chart_builder_input["dataframe_id"]
		column_names = chart_builder_input["column_names"]
		row_names = chart_builder_input["row_names"]

		try:
			dataframe = DataFrame.objects.get(pk = dataframe_id)
		except Exception,e:
			context['debug'] = str(e)
			return self.render_to_response(context)

		chart_type = chart_selector(dataframe, chart_builder_input)
# 		context["error_message"] = dataframe.columns
		
		### No Chart ###
		if(chart_type == "none"):
			context['contents'] = ""
			
		### Pie Chart ###
		elif(chart_type == "pieChart"):
			# Get either the column or row name (whichever was specified)
			column_name = (row_names[:1] or column_names[:1])[0]

			query_results, tmp = dataframe.query_results(
				"SELECT %s `key`, count(*) y FROM %s GROUP BY 1" 
				% (column_name, dataframe.db_table_name)
			);
			
			chart_data = list(query_results)

			context['chart_data'] = json.dumps(chart_data, cls=CustomJSONEncoder)
			context['chartType'] = 'pieChart';
# 			context['error_message'] = chart_data

		### Line Chart ###		
		elif(chart_type == "lineChart"):
		
			query_results, query_headings = dataframe.query_results(
				"SELECT %s x, %s y \n\
				FROM %s \n\
				ORDER BY %s" 
				% (column_names[0], row_names[0], dataframe.db_table_name, column_names[0] )
			);

			query_results_as_list = list(query_results)
 			chart_data = [{"key": row_names[0], "values":  query_results_as_list}]

			context['xaxis_label'] = column_names[0]
			context['xaxis_type'] = 'date' if hasattr(chart_data[0]["values"][0]["x"], "isoformat") else 'other'
			context['yaxis_label'] = row_names[0]
			context['chartType'] = 'lineChart'

			context['chart_data'] = json.dumps(chart_data, cls=CustomJSONEncoder)
		else:
			context['error_message'] = "That analysis type hasn't been implemented yet"
			
		context["debug_mode"] = request.GET.get('debug_mode')
		return self.render_to_response(context)

