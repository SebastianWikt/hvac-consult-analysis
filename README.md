# Service Call Recording Analysis Tool

A web application for analyzing service call recordings with automated transcription, compliance scoring, and detailed performance insights. Built for HVAC service companies to improve sales effectiveness and customer interactions.

Note: Sensitive customer information is *removed* to display as a work sample. This is a synthetic reconstruction based on multiple HVAC service calls. No real customer data is included.

## Overview

This tool processes service call recordings to provide:

- **Automated transcription** with speaker identification and timestamps
- **Compliance scoring** across key sales stages with weighted metrics
- **Custom analysis** with actionable recommendations
- **Interactive visualization** of call flow and performance metrics

## Tools Used

- **Bootstrap 5** - Responsive UI framework and components
- **Node.js** - JavaScript runtime for build processes
- **Python 3.8+** - Audio processing and analysis pipeline
- **Django** - Web framework for full-stack development (optional)
- **AssemblyAI** - Speech-to-text transcription service
- **Vercel** - Static site hosting and deployment platform (CI/CD)
- **Kiro** - Primary development environment

## Architecture

### Frontend

- **Vanilla JavaScript** with Bootstrap 5 for responsive UI
- **Synchronized scrolling** with intersection observers
- **Dynamic content generation** from JSON data

### Backend Options

- **Static Site Generation**: Node.js build process for Vercel deployment
- **Django Framework**: Full-featured web application (optional)
- **Python Processing**: Audio transcription and analysis pipeline

## Customization

### Weighted Scoring Algorithm

The system calculates weighted scores by multiplying each stage score by its weight, then computing the percentage based on weighted totals. This ensures critical sales activities have proportional impact on overall performance.

### Adjusting Weights

Modify the `sectionWeights` object in `service_call_analyzer/static/js/app.js`:

```javascript
const sectionWeights = {
  "Upsell Attempts": 3, // Highest priority
  "Problem Diagnosis": 2, // High priority
  "Solution Explanation": 2, // High priority
  Introduction: 1, // Standard weight
  // ... other stages
};
```

## Quick Start

```bash
# Clone the repository
git clone <repository-url>
cd service-call-analyzer

# Install Node.js dependencies
npm install

# Build the static site
npm run build

# Start local development server
npm run dev
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


