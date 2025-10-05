import os
from django.shortcuts import render
from django.views.generic import TemplateView
from django.conf import settings
from django.contrib import messages
from .data_processing import CallData, CustomAnalysis


class MainAnalysisView(TemplateView):
    template_name = 'call_analysis/main.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        try:
            # Load call data
            call_data_path = os.path.join(settings.MEDIA_ROOT, 'call.json')
            call_data = CallData.from_json_file(call_data_path)
            
            # Load custom analysis
            custom_analysis_path = os.path.join(settings.STATICFILES_DIRS[0], 'custom_analysis.json')
            custom_analysis = CustomAnalysis(custom_analysis_path)
            
            # Get structured data
            stages = call_data.get_stages()
            utterances_by_stage = call_data.get_all_utterances_grouped_by_stage()
            compliance_data = call_data.get_all_compliance_data()
            custom_analysis_data = custom_analysis.get_all_stage_analysis()
            call_summary = call_data.get_call_summary()
            
            # Prepare context data
            context.update({
                'title': 'Service Call Analysis',
                'call_meta': call_data.meta,
                'call_summary': call_summary,
                'stages': stages,
                'utterances_by_stage': utterances_by_stage,
                'compliance_data': compliance_data,
                'custom_analysis': custom_analysis_data,
                'has_data': True
            })
            
        except FileNotFoundError as e:
            context.update({
                'title': 'Service Call Analysis - Error',
                'error_message': f'Data file not found: {str(e)}',
                'has_data': False
            })
            
        except Exception as e:
            context.update({
                'title': 'Service Call Analysis - Error',
                'error_message': f'Error loading data: {str(e)}',
                'has_data': False
            })
        
        return context
