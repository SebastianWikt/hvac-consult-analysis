#!/usr/bin/env python3
"""
Static site generator for the Service Call Analyzer
Converts Django templates to static HTML for Vercel deployment
"""

import os
import json
import shutil
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from collections import defaultdict

def load_call_data():
    """Load call data from JSON file"""
    with open('service_call_analyzer/media/call.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def load_custom_analysis():
    """Load custom analysis data"""
    with open('service_call_analyzer/static/custom_analysis.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def process_call_data(data):
    """Process call data similar to Django data processing"""
    # Extract stages
    stages = []
    for check in data.get('compliance_check', []):
        stage = check.get('stage')
        if stage and stage not in stages:
            stages.append(stage)
    
    # Group utterances by stage
    utterances_by_stage = defaultdict(list)
    for utterance in data.get('utterances', []):
        stage = utterance.get('stage', 'General')
        utterances_by_stage[stage].append(utterance)
    
    # Sort utterances within each stage chronologically
    for stage in utterances_by_stage:
        utterances_by_stage[stage].sort(key=lambda x: x.get('start', 0))
    
    # Process compliance data
    compliance_data = {}
    for check in data.get('compliance_check', []):
        stage = check.get('stage')
        if stage:
            compliance_data[stage] = {
                'score': check.get('score', 0),
                'max_score': check.get('max', 5),
                'evidence': check.get('evidence', ''),
                'suggestion': check.get('suggestion', '')
            }
    
    # Calculate summary
    total_utterances = len(data.get('utterances', []))
    total_compliance_score = sum(check.get('score', 0) for check in data.get('compliance_check', []))
    max_compliance_score = sum(check.get('max', 5) for check in data.get('compliance_check', []))
    
    call_summary = {
        'call_type': data.get('meta', {}).get('call_type', 'Unknown'),
        'date_analyzed': data.get('meta', {}).get('date_analyzed', 'Unknown'),
        'total_utterances': total_utterances,
        'total_stages': len(stages),
        'stages': stages,
        'compliance_score': total_compliance_score,
        'max_compliance_score': max_compliance_score,
        'compliance_percentage': (total_compliance_score / max_compliance_score * 100) if max_compliance_score > 0 else 0
    }
    
    return {
        'stages': stages,
        'utterances_by_stage': dict(utterances_by_stage),
        'compliance_data': compliance_data,
        'call_summary': call_summary,
        'call_meta': data.get('meta', {})
    }

def widthratio(value, max_value, scale):
    """Django widthratio template filter equivalent"""
    if max_value == 0:
        return 0
    return int((value / max_value) * scale)

def floatformat(value, precision=0):
    """Django floatformat template filter equivalent"""
    if precision == 0:
        return str(int(float(value)))
    return f"{float(value):.{precision}f}"

def generate_static_site():
    """Generate static HTML files"""
    # Create output directory
    output_dir = Path('static')
    output_dir.mkdir(exist_ok=True)
    
    # Copy static assets
    static_src = Path('service_call_analyzer/static')
    if static_src.exists():
        shutil.copytree(static_src, output_dir / 'static', dirs_exist_ok=True)
    
    # Load data
    call_data = load_call_data()
    custom_analysis = load_custom_analysis()
    processed_data = process_call_data(call_data)
    
    # Setup Jinja2 environment
    template_dirs = [Path('service_call_analyzer/templates'), Path('templates')]
    env = Environment(loader=FileSystemLoader(template_dirs))
    
    # Add custom filters
    env.filters['widthratio'] = widthratio
    env.filters['floatformat'] = floatformat
    env.filters['lookup'] = lambda d, key: d.get(key, {})
    
    # Load templates
    base_template = env.get_template('static_base.html')
    main_template = env.get_template('call_analysis/main.html')
    
    # Prepare template context
    context = {
        'title': 'Service Call Analysis',
        'has_data': True,
        'stages': processed_data['stages'],
        'utterances_by_stage': processed_data['utterances_by_stage'],
        'compliance_data': processed_data['compliance_data'],
        'custom_analysis': custom_analysis.get('stages', {}),
        'call_summary': processed_data['call_summary'],
        'call_meta': processed_data['call_meta']
    }
    
    # Render main page
    html_content = main_template.render(**context)
    
    # Create a simple base template wrapper
    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{context['title']}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.7.2/font/bootstrap-icons.css" rel="stylesheet">
    <link href="/static/css/main.css" rel="stylesheet">
</head>
<body>
    <div class="main-content">
        {html_content}
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="/static/js/main.js"></script>
</body>
</html>"""
    
    # Write index.html
    with open(output_dir / 'index.html', 'w', encoding='utf-8') as f:
        f.write(full_html)
    
    print("Static site generated successfully!")
    print(f"Output directory: {output_dir.absolute()}")

if __name__ == '__main__':
    generate_static_site()