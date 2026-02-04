#!/usr/bin/env python3
"""
Demo script to show detailed road damage analysis capabilities
"""

import json
from datetime import datetime
from utils.damage_analysis import DamageAnalyzer

def create_demo_damage_data():
    """Create sample damage data to demonstrate detailed analysis"""
    
    # Sample damage detections (simulating what would come from YOLO)
    sample_damages = [
        {
            'damage_type': 'D40_Pothole',
            'confidence': 0.85,
            'bbox': [100, 150, 180, 220],  # x1, y1, x2, y2
        },
        {
            'damage_type': 'D00_Longitudinal_Crack',
            'confidence': 0.72,
            'bbox': [200, 100, 250, 300],
        },
        {
            'damage_type': 'D20_Alligator_Crack',
            'confidence': 0.91,
            'bbox': [300, 200, 450, 350],
        },
        {
            'damage_type': 'D10_Transverse_Crack',
            'confidence': 0.68,
            'bbox': [50, 400, 200, 430],
        }
    ]
    
    return sample_damages

def generate_detailed_analysis_demo():
    """Generate a comprehensive damage analysis demo"""
    
    print("🚗 Road Damage Detection - Detailed Analysis Demo")
    print("=" * 60)
    
    # Initialize analyzer
    analyzer = DamageAnalyzer()
    
    # Create sample damage data
    sample_damages = create_demo_damage_data()
    image_shape = (640, 640, 3)  # Sample image dimensions
    
    print(f"\n📊 Analyzing {len(sample_damages)} detected damages...")
    
    # Analyze each damage in detail
    detailed_analyses = []
    total_cost = 0
    total_time = 0
    
    for i, damage in enumerate(sample_damages, 1):
        print(f"\n--- Damage {i}: {damage['damage_type']} ---")
        
        analysis = analyzer.analyze_single_damage(damage, image_shape)
        detailed_analyses.append(analysis)
        
        # Display key information
        print(f"Severity: {analysis['severity'].upper()}")
        print(f"Area: {analysis['area_sqm']} m²")
        print(f"Repair Cost: ${analysis['repair_cost']:,.2f}")
        print(f"Repair Time: {analysis['repair_time_hours']} hours ({analysis['repair_days']} days)")
        print(f"Priority: {analysis['priority']['action']} - {analysis['priority']['timeline']}")
        print(f"Method: {analysis['repair_method']}")
        print(f"Materials: {analysis['materials_needed']}")
        print(f"Crew Size: {analysis['crew_size']['total']} workers")
        
        total_cost += analysis['repair_cost']
        total_time += analysis['repair_time_hours']
    
    # Generate area summary
    area_name = "Highway A1 - Section 5"
    total_images = 50  # Simulated survey size
    
    print(f"\n" + "=" * 60)
    print(f"📋 COMPREHENSIVE AREA ANALYSIS: {area_name}")
    print("=" * 60)
    
    area_analysis = analyzer.generate_area_summary(area_name, detailed_analyses, total_images)
    
    # Display comprehensive results
    print(f"\n🏁 OVERALL CONDITION: {area_analysis['overall_condition']}")
    print(f"📝 Description: {area_analysis['condition_description']}")
    
    stats = area_analysis['summary_statistics']
    print(f"\n📊 SUMMARY STATISTICS:")
    print(f"   • Total Images Surveyed: {stats['total_images_surveyed']}")
    print(f"   • Damaged Locations: {stats['damaged_locations']}")
    print(f"   • Damage Rate: {stats['damage_rate_percentage']:.1f}%")
    print(f"   • Total Damaged Area: {stats['total_damaged_area_sqm']:.2f} m²")
    print(f"   • Total Repair Cost: ${stats['total_repair_cost_usd']:,.2f}")
    print(f"   • Total Repair Time: {stats['total_repair_time_hours']:.1f} hours")
    print(f"   • Project Duration: {stats['estimated_project_duration_days']} days")
    
    # Budget breakdown
    budget = area_analysis['budget_breakdown']
    print(f"\n💰 BUDGET BREAKDOWN:")
    for category, amount in budget['categories'].items():
        print(f"   • {category.replace('_', ' ').title()}: ${amount:,.2f}")
    print(f"   • TOTAL BUDGET: ${budget['total_budget']:,.2f}")
    
    # Project timeline
    timeline = area_analysis['project_timeline']
    print(f"\n📅 PROJECT TIMELINE:")
    phases = ['immediate_phase', 'urgent_phase', 'scheduled_phase', 'preventive_phase']
    for phase in phases:
        phase_data = timeline.get(phase, {})
        if phase_data.get('damages'):
            print(f"   • {phase_data['description']}: {phase_data['duration_days']} days ({len(phase_data['damages'])} repairs)")
    
    # Resource requirements
    resources = area_analysis['resource_requirements']
    print(f"\n👷 RESOURCE REQUIREMENTS:")
    print(f"   • Peak Crew Size: {resources['peak_crew_size']} workers")
    print(f"   • Equipment Types: {resources['total_equipment_types']}")
    print(f"   • Trucks Needed: {resources['estimated_trucks_needed']}")
    print(f"   • Equipment: {', '.join(resources['equipment_list'][:5])}...")
    
    # Risk assessment
    risk = area_analysis['risk_assessment']
    print(f"\n⚠️  RISK ASSESSMENT:")
    print(f"   • Risk Level: {risk['risk_level']}")
    print(f"   • Risk Score: {risk['risk_score']}/20")
    print(f"   • Monitoring Frequency: {risk['monitoring_frequency']}")
    print(f"   • Key Risk Factors:")
    for factor in risk['factors'][:3]:
        print(f"     - {factor}")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    for i, rec in enumerate(area_analysis['recommendations'][:5], 1):
        print(f"   {i}. {rec['priority']}: {rec['action']}")
        print(f"      Reason: {rec['reason']}")
    
    # Save detailed report
    report_data = {
        'area_analysis': area_analysis,
        'detailed_damages': detailed_analyses,
        'generated_at': datetime.now().isoformat()
    }
    
    report_file = f"demo_detailed_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump(report_data, f, indent=2)
    
    print(f"\n📄 Detailed report saved: {report_file}")
    
    # Generate HTML summary
    html_summary = generate_html_summary(area_analysis, detailed_analyses)
    html_file = f"demo_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    
    with open(html_file, 'w') as f:
        f.write(html_summary)
    
    print(f"🌐 HTML report generated: {html_file}")
    print(f"\n🎉 Demo complete! This shows the level of detail available for each damaged road area.")

def generate_html_summary(area_analysis, detailed_damages):
    """Generate a simple HTML summary"""
    
    stats = area_analysis['summary_statistics']
    budget = area_analysis['budget_breakdown']
    
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Road Damage Analysis - {area_analysis['area_name']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 10px; }}
        .stats {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin: 20px 0; }}
        .stat-card {{ background: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center; }}
        .condition-{area_analysis['overall_condition'].lower()} {{ 
            background: {'#d4edda' if area_analysis['overall_condition'] == 'EXCELLENT' else '#fff3cd' if area_analysis['overall_condition'] == 'GOOD' else '#f8d7da'}; 
        }}
        .damage-item {{ background: white; margin: 10px 0; padding: 15px; border-left: 4px solid #007bff; }}
        .budget-item {{ display: flex; justify-content: space-between; padding: 5px 0; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🚗 Road Damage Analysis Report</h1>
        <h2>{area_analysis['area_name']}</h2>
        <p>Survey Date: {area_analysis['survey_date'][:10]}</p>
    </div>
    
    <div class="condition-{area_analysis['overall_condition'].lower()}" style="padding: 20px; margin: 20px 0; border-radius: 10px;">
        <h2>Overall Condition: {area_analysis['overall_condition']}</h2>
        <p>{area_analysis['condition_description']}</p>
    </div>
    
    <div class="stats">
        <div class="stat-card">
            <h3>{stats['total_images_surveyed']}</h3>
            <p>Images Surveyed</p>
        </div>
        <div class="stat-card">
            <h3>{stats['damaged_locations']}</h3>
            <p>Damaged Locations</p>
        </div>
        <div class="stat-card">
            <h3>${stats['total_repair_cost_usd']:,.0f}</h3>
            <p>Total Repair Cost</p>
        </div>
        <div class="stat-card">
            <h3>{stats['damage_rate_percentage']:.1f}%</h3>
            <p>Damage Rate</p>
        </div>
        <div class="stat-card">
            <h3>{stats['total_repair_time_hours']:.0f} hours</h3>
            <p>Repair Time</p>
        </div>
        <div class="stat-card">
            <h3>{stats['estimated_project_duration_days']} days</h3>
            <p>Project Duration</p>
        </div>
    </div>
    
    <h2>💰 Budget Breakdown</h2>
    <div style="background: white; padding: 20px; border-radius: 10px;">
    """
    
    for category, amount in budget['categories'].items():
        html += f'<div class="budget-item"><span>{category.replace("_", " ").title()}:</span><span>${amount:,.2f}</span></div>'
    
    html += f"""
        <hr>
        <div class="budget-item"><strong><span>Total Budget:</span><span>${budget['total_budget']:,.2f}</span></strong></div>
    </div>
    
    <h2>🔧 Detailed Damage Analysis</h2>
    """
    
    for i, damage in enumerate(detailed_damages, 1):
        priority_color = {1: '#dc3545', 2: '#fd7e14', 3: '#ffc107', 4: '#28a745'}.get(damage['priority']['level'], '#6c757d')
        
        html += f"""
        <div class="damage-item" style="border-left-color: {priority_color};">
            <h4>Damage {i}: {damage['damage_type'].replace('_', ' ')}</h4>
            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px;">
                <div><strong>Severity:</strong> {damage['severity'].title()}</div>
                <div><strong>Area:</strong> {damage['area_sqm']} m²</div>
                <div><strong>Cost:</strong> ${damage['repair_cost']:,.0f}</div>
                <div><strong>Time:</strong> {damage['repair_time_hours']} hours</div>
            </div>
            <p><strong>Method:</strong> {damage['repair_method']}</p>
            <p><strong>Materials:</strong> {damage['materials_needed']}</p>
            <p><strong>Priority:</strong> {damage['priority']['action']} - {damage['priority']['timeline']}</p>
        </div>
        """
    
    html += """
    <h2>💡 Recommendations</h2>
    <div style="background: white; padding: 20px; border-radius: 10px;">
    """
    
    for rec in area_analysis['recommendations'][:5]:
        color = {'IMMEDIATE': '#dc3545', 'URGENT': '#fd7e14', 'STRATEGIC': '#17a2b8', 'PLANNING': '#007bff', 'PREVENTIVE': '#28a745'}.get(rec['priority'], '#6c757d')
        html += f"""
        <div style="border-left: 4px solid {color}; padding: 10px; margin: 10px 0; background: #f8f9fa;">
            <strong>{rec['priority']}:</strong> {rec['action']}<br>
            <small>{rec['reason']}</small>
        </div>
        """
    
    html += """
    </div>
    
    <footer style="margin-top: 40px; text-align: center; color: #6c757d;">
        <p>Generated by Road Damage Detection System - Detailed Analysis Engine</p>
    </footer>
</body>
</html>
    """
    
    return html

if __name__ == "__main__":
    generate_detailed_analysis_demo()