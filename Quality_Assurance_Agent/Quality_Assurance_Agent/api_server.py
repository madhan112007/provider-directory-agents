from flask import Flask, jsonify
import json
import pandas as pd
import os

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    """Root endpoint"""
    return jsonify({
        "message": "QA Metrics API Server",
        "endpoints": [
            "/api/metrics",
            "/api/dashboard/summary",
            "/api/dashboard/error-distribution",
            "/api/dashboard/risk-breakdown",
            "/api/dashboard/confidence-breakdown",
            "/api/dashboard/action-split",
            "/api/providers/high-risk",
            "/api/providers/manual-review"
        ]
    })

@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    """Get overall run-level metrics"""
    try:
        file_path = os.path.join(os.path.dirname(__file__), 'qa_metrics.json')
        print(f"Looking for file at: {file_path}")
        print(f"File exists: {os.path.exists(file_path)}")
        with open(file_path, 'r') as f:
            return jsonify(json.load(f))
    except FileNotFoundError as e:
        return jsonify({"error": f"Metrics file not found: {str(e)}"}), 404
    except Exception as e:
        return jsonify({"error": f"Error reading metrics: {str(e)}"}), 500

@app.route('/api/dashboard/summary', methods=['GET'])
def get_dashboard_summary():
    """Get summary stats for dashboard"""
    try:
        with open('qa_metrics.json', 'r') as f:
            metrics = json.load(f)
    except FileNotFoundError:
        return jsonify({"error": "Metrics file not found. Run test_agentic.py first."}), 404
    
    return jsonify({
        "total_providers": metrics['total_processed'],
        "auto_resolved": metrics['auto_resolve_count'],
        "manual_review": metrics['manual_review_count'],
        "review_rate": metrics['manual_review_rate'],
        "within_target": metrics['within_target']
    })

@app.route('/api/dashboard/error-distribution', methods=['GET'])
def get_error_distribution():
    """Get error type distribution for charts"""
    try:
        with open('qa_metrics.json', 'r') as f:
            metrics = json.load(f)
        return jsonify(metrics['top_error_types'])
    except FileNotFoundError:
        return jsonify({"error": "Metrics file not found. Run test_agentic.py first."}), 404

@app.route('/api/dashboard/risk-breakdown', methods=['GET'])
def get_risk_breakdown():
    """Get risk score breakdown"""
    try:
        df = pd.read_csv('qa_results.csv')
        risk_ranges = {
            "Low (0-30)": int(len(df[df['risk_score'] <= 30])),
            "Medium (31-60)": int(len(df[(df['risk_score'] > 30) & (df['risk_score'] <= 60)])),
            "High (61-100)": int(len(df[df['risk_score'] > 60]))
        }
        return jsonify(risk_ranges)
    except FileNotFoundError:
        return jsonify({"error": "Results file not found. Run test_agentic.py first."}), 404
    except Exception as e:
        return jsonify({"error": f"Error processing risk breakdown: {str(e)}"}), 500

@app.route('/api/dashboard/confidence-breakdown', methods=['GET'])
def get_confidence_breakdown():
    """Get confidence score breakdown"""
    try:
        df = pd.read_csv('qa_results.csv')
    except FileNotFoundError:
        return jsonify({"error": "Results file not found. Run test_agentic.py first."}), 404
    
    confidence_ranges = {
        "Low (0-50)": len(df[df['confidence_score'] <= 50]),
        "Medium (51-75)": len(df[(df['confidence_score'] > 50) & (df['confidence_score'] <= 75)]),
        "High (76-100)": len(df[df['confidence_score'] > 75])
    }
    
    return jsonify(confidence_ranges)

@app.route('/api/dashboard/action-split', methods=['GET'])
def get_action_split():
    """Get action distribution"""
    try:
        df = pd.read_csv('qa_results.csv')
    except FileNotFoundError:
        return jsonify({"error": "Results file not found. Run test_agentic.py first."}), 404
    
    return jsonify({
        "auto_resolve": len(df[df['action'] == 'auto_resolve']),
        "manual_review": len(df[df['action'] == 'manual_review'])
    })

@app.route('/api/providers/high-risk', methods=['GET'])
def get_high_risk_providers():
    """Get list of high-risk providers"""
    try:
        df = pd.read_csv('qa_results.csv')
    except FileNotFoundError:
        return jsonify({"error": "Results file not found. Run test_agentic.py first."}), 404
    high_risk = df[df['risk_score'] >= 60].sort_values('risk_score', ascending=False)
    
    return jsonify(high_risk[['name', 'risk_score', 'confidence_score', 'action', 'red_flags']].to_dict('records'))

@app.route('/api/providers/manual-review', methods=['GET'])
def get_manual_review_providers():
    """Get providers needing manual review"""
    try:
        df = pd.read_csv('qa_results.csv')
    except FileNotFoundError:
        return jsonify({"error": "Results file not found. Run test_agentic.py first."}), 404
    manual = df[df['action'] == 'manual_review']
    
    return jsonify(manual[['name', 'risk_score', 'confidence_score', 'impact_score', 'red_flags']].to_dict('records'))

if __name__ == '__main__':
    print("\n" + "="*50)
    print("QA Metrics API Server Starting...")
    print("="*50)
    print("\nServer: http://localhost:5003")
    print("\nAvailable endpoints:")
    print("  GET / - API info")
    print("  GET /api/metrics - Overall metrics")
    print("  GET /api/dashboard/summary - Dashboard summary")
    print("  GET /api/dashboard/error-distribution - Error types")
    print("  GET /api/dashboard/risk-breakdown - Risk distribution")
    print("  GET /api/dashboard/confidence-breakdown - Confidence distribution")
    print("  GET /api/dashboard/action-split - Action distribution")
    print("  GET /api/providers/high-risk - High risk providers")
    print("  GET /api/providers/manual-review - Manual review list")
    print("\n" + "="*50 + "\n")
    app.run(host='0.0.0.0', port=5003, debug=True)
