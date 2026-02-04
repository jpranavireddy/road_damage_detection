"""
Detailed Damage Analysis and Repair Estimation System
"""

import json
from datetime import datetime, timedelta
import math

class DamageAnalyzer:
    """Comprehensive damage analysis and repair estimation"""
    
    def __init__(self):
        # Damage severity levels
        self.severity_levels = {
            'minor': {'threshold': 0.3, 'multiplier': 1.0},
            'moderate': {'threshold': 0.6, 'multiplier': 1.5},
            'severe': {'threshold': 0.8, 'multiplier': 2.5},
            'critical': {'threshold': 1.0, 'multiplier': 4.0}
        }
        
        # Repair cost estimates (per square meter in INR - Indian Rupees)
        self.repair_costs = {
            'D00_Longitudinal_Crack': {
                'minor': {'cost_per_m': 1200, 'material': 'Crack sealing compound', 'method': 'Hot pour crack sealing'},
                'moderate': {'cost_per_m': 2000, 'material': 'Rubberized crack filler', 'method': 'Routing and sealing'},
                'severe': {'cost_per_m': 3600, 'material': 'Asphalt patching mix', 'method': 'Mill and overlay'},
                'critical': {'cost_per_m': 6800, 'material': 'Full depth asphalt', 'method': 'Complete reconstruction'}
            },
            'D10_Transverse_Crack': {
                'minor': {'cost_per_m': 1440, 'material': 'Crack sealing compound', 'method': 'Surface sealing'},
                'moderate': {'cost_per_m': 2400, 'material': 'Polymer-modified sealant', 'method': 'Crack routing and sealing'},
                'severe': {'cost_per_m': 4000, 'material': 'Asphalt overlay', 'method': 'Mill and resurface'},
                'critical': {'cost_per_m': 7200, 'material': 'Full reconstruction', 'method': 'Complete rebuild'}
            },
            'D20_Alligator_Crack': {
                'minor': {'cost_per_m': 2800, 'material': 'Micro-surfacing', 'method': 'Surface treatment'},
                'moderate': {'cost_per_m': 5200, 'material': 'Thin overlay', 'method': '2-inch overlay'},
                'severe': {'cost_per_m': 9600, 'material': 'Full depth patching', 'method': 'Remove and replace'},
                'critical': {'cost_per_m': 16000, 'material': 'Complete reconstruction', 'method': 'Full depth reconstruction'}
            },
            'D40_Pothole': {
                'minor': {'cost_per_m': 2000, 'material': 'Cold patch asphalt', 'method': 'Temporary patching'},
                'moderate': {'cost_per_m': 3600, 'material': 'Hot mix asphalt', 'method': 'Permanent patching'},
                'severe': {'cost_per_m': 6000, 'material': 'Full depth patch', 'method': 'Saw cut and replace'},
                'critical': {'cost_per_m': 12000, 'material': 'Structural repair', 'method': 'Base repair and overlay'}
            },
            'Repair': {
                'minor': {'cost_per_m': 800, 'material': 'Inspection only', 'method': 'Quality assessment'},
                'moderate': {'cost_per_m': 1600, 'material': 'Touch-up materials', 'method': 'Minor repairs'},
                'severe': {'cost_per_m': 3200, 'material': 'Rework materials', 'method': 'Repair rework'},
                'critical': {'cost_per_m': 6400, 'material': 'Complete redo', 'method': 'Full reconstruction'}
            },
            'Block_Crack': {
                'minor': {'cost_per_m': 1600, 'material': 'Crack sealing', 'method': 'Preventive sealing'},
                'moderate': {'cost_per_m': 3200, 'material': 'Overlay preparation', 'method': 'Surface preparation'},
                'severe': {'cost_per_m': 5600, 'material': 'Milling and overlay', 'method': 'Remove and replace'},
                'critical': {'cost_per_m': 10400, 'material': 'Full reconstruction', 'method': 'Complete rebuild'}
            }
        }
        
        # Repair time estimates (hours per square meter)
        self.repair_times = {
            'D00_Longitudinal_Crack': {'minor': 0.5, 'moderate': 1.0, 'severe': 2.5, 'critical': 6.0},
            'D10_Transverse_Crack': {'minor': 0.6, 'moderate': 1.2, 'severe': 3.0, 'critical': 7.0},
            'D20_Alligator_Crack': {'minor': 1.5, 'moderate': 3.0, 'severe': 6.0, 'critical': 12.0},
            'D40_Pothole': {'minor': 1.0, 'moderate': 2.0, 'severe': 4.0, 'critical': 8.0},
            'Repair': {'minor': 0.3, 'moderate': 0.8, 'severe': 2.0, 'critical': 5.0},
            'Block_Crack': {'minor': 0.8, 'moderate': 1.5, 'severe': 3.5, 'critical': 8.0}
        }
        
        # Priority levels
        self.priority_matrix = {
            'critical': {'level': 1, 'action': 'IMMEDIATE', 'timeline': '24-48 hours', 'risk': 'High safety risk'},
            'severe': {'level': 2, 'action': 'URGENT', 'timeline': '1-2 weeks', 'risk': 'Moderate safety risk'},
            'moderate': {'level': 3, 'action': 'SCHEDULED', 'timeline': '1-3 months', 'risk': 'Low safety risk'},
            'minor': {'level': 4, 'action': 'PREVENTIVE', 'timeline': '3-6 months', 'risk': 'Minimal risk'}
        }
    
    def calculate_damage_area(self, bbox, image_shape, pixel_to_meter_ratio=0.01):
        """Calculate damage area in square meters from bounding box"""
        if not bbox or len(bbox) < 4:
            return 0.1  # Default small area
        
        x1, y1, x2, y2 = bbox
        width_pixels = abs(x2 - x1)
        height_pixels = abs(y2 - y1)
        
        # Convert pixels to meters (approximate)
        width_meters = width_pixels * pixel_to_meter_ratio
        height_meters = height_pixels * pixel_to_meter_ratio
        
        return width_meters * height_meters
    
    def determine_severity(self, confidence, damage_type, area_sqm):
        """Determine damage severity based on confidence, type, and area"""
        # Base severity from confidence
        if confidence >= 0.8:
            base_severity = 'severe'
        elif confidence >= 0.6:
            base_severity = 'moderate'
        elif confidence >= 0.4:
            base_severity = 'minor'
        else:
            base_severity = 'minor'
        
        # Adjust based on damage type and area
        if damage_type in ['D20_Alligator_Crack', 'D40_Pothole']:
            if area_sqm > 2.0:
                if base_severity == 'severe':
                    return 'critical'
                elif base_severity == 'moderate':
                    return 'severe'
            elif area_sqm > 0.5:
                if base_severity == 'minor':
                    return 'moderate'
        
        return base_severity
    
    def analyze_single_damage(self, detection, image_shape):
        """Analyze a single damage detection"""
        damage_type = detection.get('damage_type', 'Unknown')
        confidence = detection.get('confidence', 0.5)
        bbox = detection.get('bbox', [0, 0, 100, 100])
        
        # Calculate damage area
        area_sqm = self.calculate_damage_area(bbox, image_shape)
        
        # Determine severity
        severity = self.determine_severity(confidence, damage_type, area_sqm)
        
        # Get repair information
        repair_info = self.repair_costs.get(damage_type, self.repair_costs['D40_Pothole'])[severity]
        repair_time = self.repair_times.get(damage_type, self.repair_times['D40_Pothole'])[severity]
        priority_info = self.priority_matrix[severity]
        
        # Calculate costs and time
        total_cost = area_sqm * repair_info['cost_per_m']
        total_time_hours = area_sqm * repair_time
        
        # Estimate crew size and equipment
        crew_size = self.estimate_crew_size(damage_type, severity, area_sqm)
        equipment_needed = self.get_equipment_list(damage_type, severity)
        
        return {
            'damage_type': damage_type,
            'severity': severity,
            'confidence': confidence,
            'area_sqm': round(area_sqm, 2),
            'bbox': bbox,
            'repair_cost': round(total_cost, 2),
            'repair_time_hours': round(total_time_hours, 1),
            'repair_days': math.ceil(total_time_hours / 8),  # 8-hour work days
            'priority': priority_info,
            'repair_method': repair_info['method'],
            'materials_needed': repair_info['material'],
            'crew_size': crew_size,
            'equipment_needed': equipment_needed,
            'safety_requirements': self.get_safety_requirements(damage_type, severity),
            'weather_constraints': self.get_weather_constraints(damage_type),
            'traffic_impact': self.assess_traffic_impact(damage_type, severity, area_sqm)
        }
    
    def estimate_crew_size(self, damage_type, severity, area_sqm):
        """Estimate required crew size"""
        base_crew = {
            'minor': 2,
            'moderate': 3,
            'severe': 4,
            'critical': 6
        }
        
        crew = base_crew[severity]
        
        # Adjust for large areas
        if area_sqm > 5.0:
            crew += 2
        elif area_sqm > 2.0:
            crew += 1
        
        return {
            'total': crew,
            'roles': self.get_crew_roles(damage_type, severity, crew)
        }
    
    def get_crew_roles(self, damage_type, severity, total_crew):
        """Define crew roles based on damage type and severity"""
        if severity in ['critical', 'severe']:
            return {
                'supervisor': 1,
                'equipment_operator': 1 if total_crew >= 3 else 0,
                'skilled_workers': max(2, total_crew - 2),
                'traffic_control': 1 if total_crew >= 4 else 0,
                'safety_officer': 1 if total_crew >= 5 else 0
            }
        else:
            return {
                'supervisor': 1,
                'skilled_workers': total_crew - 1,
                'traffic_control': 1 if total_crew >= 3 else 0
            }
    
    def get_equipment_list(self, damage_type, severity):
        """Get required equipment list"""
        base_equipment = ['Hand tools', 'Safety equipment', 'Traffic cones']
        
        if severity in ['severe', 'critical']:
            if damage_type in ['D20_Alligator_Crack', 'D40_Pothole']:
                return base_equipment + [
                    'Asphalt saw', 'Jackhammer', 'Compactor', 
                    'Hot mix truck', 'Roller', 'Crack router'
                ]
            else:
                return base_equipment + [
                    'Crack router', 'Sealant applicator', 
                    'Air compressor', 'Heating kettle'
                ]
        else:
            return base_equipment + ['Crack sealing equipment', 'Cleaning tools']
    
    def get_safety_requirements(self, damage_type, severity):
        """Define safety requirements"""
        base_safety = [
            'High-visibility clothing',
            'Hard hats',
            'Safety glasses',
            'Work zone setup'
        ]
        
        if severity in ['severe', 'critical']:
            return base_safety + [
                'Traffic control plan',
                'Flaggers',
                'Temporary barriers',
                'Warning signs',
                'Emergency response plan'
            ]
        else:
            return base_safety + ['Basic traffic control', 'Warning signs']
    
    def get_weather_constraints(self, damage_type):
        """Define weather constraints for repairs"""
        return {
            'temperature': {
                'min': 40,  # Fahrenheit
                'max': 100,
                'optimal': '50-85°F'
            },
            'conditions': [
                'No precipitation during work',
                'Dry surface required',
                'Wind speed < 25 mph for sealants',
                'No freezing conditions'
            ],
            'seasonal_notes': 'Best performed in spring/summer/early fall'
        }
    
    def assess_traffic_impact(self, damage_type, severity, area_sqm):
        """Assess traffic impact and lane closure requirements"""
        if severity in ['critical', 'severe'] or area_sqm > 1.0:
            return {
                'lane_closure': 'Required',
                'duration': 'Full repair duration',
                'traffic_control': 'Flaggers and signs required',
                'alternate_route': 'Recommended for major repairs',
                'peak_hour_restrictions': 'Avoid 7-9 AM and 4-6 PM'
            }
        else:
            return {
                'lane_closure': 'Partial or rolling closure',
                'duration': 'Minimal disruption',
                'traffic_control': 'Basic signage sufficient',
                'alternate_route': 'Not required',
                'peak_hour_restrictions': 'Can work during off-peak hours'
            }
    
    def generate_area_summary(self, area_name, all_damages, total_images):
        """Generate comprehensive area damage summary"""
        if not all_damages:
            return self.generate_clean_area_report(area_name, total_images)
        
        # Calculate totals
        total_cost = sum(d['repair_cost'] for d in all_damages)
        total_time_hours = sum(d['repair_time_hours'] for d in all_damages)
        total_area = sum(d['area_sqm'] for d in all_damages)
        
        # Severity distribution
        severity_counts = {}
        damage_type_counts = {}
        priority_counts = {}
        
        for damage in all_damages:
            severity = damage['severity']
            damage_type = damage['damage_type']
            priority = damage['priority']['level']
            
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            damage_type_counts[damage_type] = damage_type_counts.get(damage_type, 0) + 1
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        # Determine overall condition
        critical_count = severity_counts.get('critical', 0)
        severe_count = severity_counts.get('severe', 0)
        
        if critical_count > 0:
            overall_condition = 'CRITICAL'
            condition_description = 'Immediate attention required'
        elif severe_count > 2:
            overall_condition = 'POOR'
            condition_description = 'Urgent repairs needed'
        elif severe_count > 0 or len(all_damages) > 5:
            overall_condition = 'FAIR'
            condition_description = 'Scheduled maintenance required'
        else:
            overall_condition = 'GOOD'
            condition_description = 'Minor maintenance needed'
        
        # Calculate project timeline
        project_timeline = self.calculate_project_timeline(all_damages)
        
        # Generate recommendations
        recommendations = self.generate_recommendations(all_damages, area_name)
        
        return {
            'area_name': area_name,
            'survey_date': datetime.now().isoformat(),
            'overall_condition': overall_condition,
            'condition_description': condition_description,
            'summary_statistics': {
                'total_images_surveyed': total_images,
                'damaged_locations': len(all_damages),
                'damage_rate_percentage': round((len(all_damages) / total_images) * 100, 1),
                'total_damaged_area_sqm': round(total_area, 2),
                'total_repair_cost_usd': round(total_cost, 2),
                'total_repair_time_hours': round(total_time_hours, 1),
                'estimated_project_duration_days': project_timeline['total_days']
            },
            'severity_breakdown': severity_counts,
            'damage_type_breakdown': damage_type_counts,
            'priority_breakdown': priority_counts,
            'project_timeline': project_timeline,
            'budget_breakdown': self.generate_budget_breakdown(all_damages),
            'resource_requirements': self.calculate_total_resources(all_damages),
            'recommendations': recommendations,
            'maintenance_schedule': self.create_maintenance_schedule(all_damages),
            'risk_assessment': self.assess_overall_risk(all_damages, area_name)
        }
    
    def generate_clean_area_report(self, area_name, total_images):
        """Generate report for areas with no damage detected"""
        return {
            'area_name': area_name,
            'survey_date': datetime.now().isoformat(),
            'overall_condition': 'EXCELLENT',
            'condition_description': 'No damage detected - road in excellent condition',
            'summary_statistics': {
                'total_images_surveyed': total_images,
                'damaged_locations': 0,
                'damage_rate_percentage': 0.0,
                'total_damaged_area_sqm': 0.0,
                'total_repair_cost_usd': 0.0,
                'total_repair_time_hours': 0.0,
                'estimated_project_duration_days': 0
            },
            'recommendations': [
                'Continue regular monitoring',
                'Schedule preventive maintenance in 6-12 months',
                'Monitor for early signs of wear',
                'Maintain current maintenance practices'
            ],
            'next_inspection': (datetime.now() + timedelta(days=180)).strftime('%Y-%m-%d'),
            'maintenance_schedule': {
                'preventive_sealing': '12-18 months',
                'crack_monitoring': '6 months',
                'surface_treatment': '3-5 years'
            }
        }
    
    def calculate_project_timeline(self, all_damages):
        """Calculate realistic project timeline"""
        # Sort by priority
        priority_groups = {1: [], 2: [], 3: [], 4: []}
        for damage in all_damages:
            priority = damage['priority']['level']
            priority_groups[priority].append(damage)
        
        timeline = {
            'immediate_phase': {
                'damages': priority_groups[1],
                'duration_days': max([d['repair_days'] for d in priority_groups[1]]) if priority_groups[1] else 0,
                'description': 'Critical repairs - safety hazards'
            },
            'urgent_phase': {
                'damages': priority_groups[2],
                'duration_days': sum([d['repair_days'] for d in priority_groups[2]]) // 2,  # Parallel work
                'description': 'Urgent repairs - prevent deterioration'
            },
            'scheduled_phase': {
                'damages': priority_groups[3],
                'duration_days': sum([d['repair_days'] for d in priority_groups[3]]) // 3,  # More parallel work
                'description': 'Scheduled maintenance'
            },
            'preventive_phase': {
                'damages': priority_groups[4],
                'duration_days': sum([d['repair_days'] for d in priority_groups[4]]) // 4,  # Efficient batching
                'description': 'Preventive maintenance'
            }
        }
        
        total_days = sum([phase['duration_days'] for phase in timeline.values()])
        timeline['total_days'] = max(total_days, 1)
        
        return timeline
    
    def generate_budget_breakdown(self, all_damages):
        """Generate detailed budget breakdown"""
        categories = {
            'materials': 0,
            'labor': 0,
            'equipment': 0,
            'traffic_control': 0,
            'contingency': 0
        }
        
        for damage in all_damages:
            repair_cost = damage['repair_cost']
            # Typical cost breakdown percentages
            categories['materials'] += repair_cost * 0.4
            categories['labor'] += repair_cost * 0.35
            categories['equipment'] += repair_cost * 0.15
            categories['traffic_control'] += repair_cost * 0.05
            categories['contingency'] += repair_cost * 0.05
        
        total = sum(categories.values())
        
        return {
            'categories': {k: round(v, 2) for k, v in categories.items()},
            'total_budget': round(total, 2),
            'cost_per_sqm_average': round(total / max(sum(d['area_sqm'] for d in all_damages), 1), 2)
        }
    
    def calculate_total_resources(self, all_damages):
        """Calculate total resource requirements"""
        max_crew = max([d['crew_size']['total'] for d in all_damages]) if all_damages else 0
        all_equipment = set()
        all_materials = set()
        
        for damage in all_damages:
            all_equipment.update(damage['equipment_needed'])
            all_materials.add(damage['materials_needed'])
        
        return {
            'peak_crew_size': max_crew,
            'total_equipment_types': len(all_equipment),
            'equipment_list': list(all_equipment),
            'material_types': list(all_materials),
            'estimated_trucks_needed': math.ceil(len(all_damages) / 5),  # 5 repairs per truck
            'storage_requirements': 'Medium' if len(all_damages) > 10 else 'Small'
        }
    
    def generate_recommendations(self, all_damages, area_name):
        """Generate actionable recommendations"""
        recommendations = []
        
        critical_count = sum(1 for d in all_damages if d['severity'] == 'critical')
        severe_count = sum(1 for d in all_damages if d['severity'] == 'severe')
        
        if critical_count > 0:
            recommendations.append({
                'priority': 'IMMEDIATE',
                'action': f'Address {critical_count} critical damage(s) within 24-48 hours',
                'reason': 'Safety hazard - risk of accidents or further deterioration'
            })
        
        if severe_count > 0:
            recommendations.append({
                'priority': 'URGENT',
                'action': f'Schedule {severe_count} severe repair(s) within 1-2 weeks',
                'reason': 'Prevent escalation to critical condition'
            })
        
        # Pattern analysis
        damage_types = [d['damage_type'] for d in all_damages]
        if damage_types.count('D20_Alligator_Crack') > 2:
            recommendations.append({
                'priority': 'STRATEGIC',
                'action': 'Consider full section overlay due to multiple alligator cracks',
                'reason': 'Multiple alligator cracks indicate structural issues'
            })
        
        if len(all_damages) > 10:
            recommendations.append({
                'priority': 'PLANNING',
                'action': 'Develop comprehensive rehabilitation plan',
                'reason': 'High damage density suggests systematic approach needed'
            })
        
        recommendations.append({
            'priority': 'PREVENTIVE',
            'action': 'Implement regular inspection schedule every 6 months',
            'reason': 'Early detection prevents costly major repairs'
        })
        
        return recommendations
    
    def create_maintenance_schedule(self, all_damages):
        """Create detailed maintenance schedule"""
        now = datetime.now()
        schedule = {}
        
        # Group by priority and create timeline
        for damage in all_damages:
            priority_level = damage['priority']['level']
            timeline = damage['priority']['timeline']
            
            if priority_level == 1:  # Critical
                start_date = now + timedelta(days=1)
            elif priority_level == 2:  # Severe
                start_date = now + timedelta(days=7)
            elif priority_level == 3:  # Moderate
                start_date = now + timedelta(days=30)
            else:  # Minor
                start_date = now + timedelta(days=90)
            
            week_key = start_date.strftime('%Y-W%U')
            if week_key not in schedule:
                schedule[week_key] = []
            
            schedule[week_key].append({
                'damage_type': damage['damage_type'],
                'severity': damage['severity'],
                'estimated_duration': damage['repair_days'],
                'cost': damage['repair_cost'],
                'crew_size': damage['crew_size']['total']
            })
        
        return schedule
    
    def assess_overall_risk(self, all_damages, area_name):
        """Assess overall risk level for the area"""
        if not all_damages:
            return {
                'risk_level': 'LOW',
                'risk_score': 1,
                'factors': ['No damage detected'],
                'mitigation': ['Continue regular monitoring']
            }
        
        risk_score = 0
        risk_factors = []
        
        # Calculate risk based on damage severity and type
        for damage in all_damages:
            if damage['severity'] == 'critical':
                risk_score += 4
                risk_factors.append(f"Critical {damage['damage_type']}")
            elif damage['severity'] == 'severe':
                risk_score += 3
                risk_factors.append(f"Severe {damage['damage_type']}")
            elif damage['severity'] == 'moderate':
                risk_score += 2
            else:
                risk_score += 1
        
        # Determine risk level
        if risk_score >= 15:
            risk_level = 'VERY HIGH'
        elif risk_score >= 10:
            risk_level = 'HIGH'
        elif risk_score >= 5:
            risk_level = 'MEDIUM'
        else:
            risk_level = 'LOW'
        
        mitigation_strategies = self.get_mitigation_strategies(risk_level, all_damages)
        
        return {
            'risk_level': risk_level,
            'risk_score': risk_score,
            'factors': risk_factors[:5],  # Top 5 risk factors
            'mitigation': mitigation_strategies,
            'monitoring_frequency': self.get_monitoring_frequency(risk_level)
        }
    
    def get_mitigation_strategies(self, risk_level, all_damages):
        """Get risk mitigation strategies"""
        strategies = []
        
        if risk_level in ['VERY HIGH', 'HIGH']:
            strategies.extend([
                'Implement immediate traffic control measures',
                'Post warning signs for hazardous areas',
                'Consider temporary road closure if necessary',
                'Expedite critical repairs',
                'Increase inspection frequency'
            ])
        elif risk_level == 'MEDIUM':
            strategies.extend([
                'Schedule repairs within recommended timeframes',
                'Monitor high-risk areas weekly',
                'Prepare contingency repair materials',
                'Plan traffic management during repairs'
            ])
        else:
            strategies.extend([
                'Continue regular monitoring',
                'Schedule preventive maintenance',
                'Document baseline conditions'
            ])
        
        return strategies
    
    def get_monitoring_frequency(self, risk_level):
        """Determine monitoring frequency based on risk level"""
        frequencies = {
            'VERY HIGH': 'Weekly',
            'HIGH': 'Bi-weekly',
            'MEDIUM': 'Monthly',
            'LOW': 'Quarterly'
        }
        return frequencies.get(risk_level, 'Quarterly')