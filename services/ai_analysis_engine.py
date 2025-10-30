import json
from datetime import datetime
from decimal import Decimal

class CasaFlowAIAnalyzer:
    def __init__(self):
        self.risk_thresholds = {
            'cibil_min': 750,
            'salary_to_emi_ratio': 0.5,
            'loan_to_value_max': 0.8
        }
    
    def analyze_application(self, application_data):
        """Comprehensive AI analysis of loan application"""
        analysis = {
            'rejection_reasons': [],
            'recommendations': [],
            'alternative_offers': [],
            'financial_health_score': 0,
            'generated_explanation': '',
            'status': 'APPROVED',  # Default status
            'risk_level': 'LOW'
        }
        
        # Perform various checks
        self._check_credit_profile(application_data, analysis)
        self._check_loan_affordability(application_data, analysis)
        self._check_loan_to_value_ratio(application_data, analysis)
        self._check_employment_stability(application_data, analysis)
        
        # Generate explanations and alternatives
        self._generate_explanation(analysis)
        self._generate_alternative_offers(application_data, analysis)
        self._calculate_financial_health_score(application_data, analysis)
        self._determine_final_status(analysis)
        
        return analysis
    
    def _check_credit_profile(self, application_data, analysis):
        cibil_score = application_data.get('cibil_score')
        if cibil_score is None or cibil_score < 10:
            analysis['rejection_reasons'].append({
                'factor': 'Credit History',
                'severity': 'High',
                'description': 'Unable to verify credit history or insufficient credit data',
                'impact': 'Cannot assess repayment behavior'
            })
            analysis['recommendations'].append({
                'action': 'Build Credit History',
                'priority': 'High',
                'description': 'Start with secured credit card and make timely payments',
                'timeline': '6-12 months'
            })
        elif cibil_score < self.risk_thresholds['cibil_min']:
            analysis['rejection_reasons'].append({
                'factor': 'Credit Score',
                'severity': 'Medium',
                'description': f'CIBIL score of {cibil_score} below minimum requirement of {self.risk_thresholds["cibil_min"]}',
                'impact': 'Higher risk of default'
            })
            analysis['recommendations'].append({
                'action': 'Improve Credit Score',
                'priority': 'High',
                'description': 'Pay existing debts on time and reduce credit utilization',
                'timeline': '3-6 months'
            })

    def _check_loan_affordability(self, application_data, analysis):
        monthly_salary = Decimal(str(application_data.get('monthly_salary', 0)))
        existing_emi = Decimal(str(application_data.get('existing_emi', 0)))
        loan_amount = Decimal(str(application_data.get('loan_amount', 0)))
        
        # Calculate affordable EMI (50% of monthly salary)
        affordable_emi = monthly_salary * Decimal('0.5')
        total_emi_obligation = affordable_emi - existing_emi
        
        if total_emi_obligation <= 0:
            analysis['rejection_reasons'].append({
                'factor': 'Debt Burden',
                'severity': 'High',
                'description': 'Existing EMI obligations exceed affordable limits',
                'impact': 'No capacity for additional loan'
            })
            return
        
        # Simple EMI calculation (8.5% annual interest, 60 months tenure)
        interest_rate = Decimal('0.085')
        tenure_months = 60
        monthly_interest = interest_rate / 12
        
        # EMI formula: P * r * (1+r)^n / ((1+r)^n - 1)
        principal = loan_amount
        emi_numerator = principal * monthly_interest * (1 + monthly_interest) ** tenure_months
        emi_denominator = (1 + monthly_interest) ** tenure_months - 1
        calculated_emi = emi_numerator / emi_denominator
        
        if calculated_emi > total_emi_obligation:
            analysis['rejection_reasons'].append({
                'factor': 'Loan Affordability',
                'severity': 'Medium',
                'description': f'Requested loan EMI (₹{calculated_emi:.0f}) exceeds affordable limit (₹{total_emi_obligation:.0f})',
                'impact': 'High debt burden ratio'
            })
            
            # Calculate suggested loan amount based on affordable EMI
            suggested_principal = (total_emi_obligation * ((1 + monthly_interest) ** tenure_months - 1))
            suggested_principal = suggested_principal / (monthly_interest * (1 + monthly_interest) ** tenure_months)
            
            analysis['alternative_offers'].append({
                'type': 'Reduced Loan Amount',
                'amount': float(suggested_principal),
                'tenure': '60 months',
                'emi': float(total_emi_obligation),
                'interest_rate': '8.5%',
                'reason': 'Better aligned with your income and existing obligations'
            })

    def _check_loan_to_value_ratio(self, application_data, analysis):
        loan_amount = Decimal(str(application_data.get('loan_amount', 0)))
        property_valuation = Decimal(str(application_data.get('property_valuation', 0)))
        
        if property_valuation > 0:
            ltv_ratio = loan_amount / property_valuation
            
            if ltv_ratio > self.risk_thresholds['loan_to_value_max']:
                analysis['rejection_reasons'].append({
                    'factor': 'Loan-to-Value Ratio',
                    'severity': 'Medium',
                    'description': f'LTV ratio of {ltv_ratio:.1%} exceeds maximum allowed {self.risk_thresholds["loan_to_value_max"]:.1%}',
                    'impact': 'Higher collateral risk'
                })
                
                # Suggest maximum loan amount based on LTV
                max_loan = property_valuation * Decimal(str(self.risk_thresholds['loan_to_value_max']))
                analysis['alternative_offers'].append({
                    'type': 'LTV Adjusted Loan',
                    'amount': float(max_loan),
                    'max_ltv': f'{self.risk_thresholds["loan_to_value_max"]:.1%}',
                    'reason': 'Maintains healthy loan-to-value ratio'
                })

    def _check_employment_stability(self, application_data, analysis):
        monthly_salary = application_data.get('monthly_salary', 0)
        company_name = application_data.get('company_name', '')
        
        # Simple employment stability check
        if monthly_salary < 30000:
            analysis['rejection_reasons'].append({
                'factor': 'Income Level',
                'severity': 'Medium',
                'description': 'Monthly salary below minimum threshold for this loan type',
                'impact': 'Limited repayment capacity'
            })
            
            analysis['alternative_offers'].append({
                'type': 'Smaller Personal Loan',
                'amount': min(500000, monthly_salary * 10),  # 10x monthly salary
                'tenure': '36 months',
                'purpose': 'Income-based smaller loan',
                'features': ['Lower amount', 'Shorter tenure']
            })

    def _generate_explanation(self, analysis):
        """Generate natural language explanation"""
        if not analysis['rejection_reasons']:
            analysis['generated_explanation'] = (
                "✅ Your application meets all our criteria! "
                "Based on our analysis, your financial profile shows strong repayment capacity "
                "and excellent creditworthiness. Congratulations!"
            )
            return
        
        explanation = "After careful review of your application, here's our assessment:\n\n"
        
        for reason in analysis['rejection_reasons']:
            explanation += f"🔴 {reason['description']} (Severity: {reason['severity']})\n"
        
        if analysis['recommendations']:
            explanation += "\n💡 We recommend the following actions:\n"
            for rec in analysis['recommendations']:
                explanation += f"• {rec['description']} (Priority: {rec['priority']})\n"
        
        if analysis['alternative_offers']:
            explanation += "\n🎯 Alternative options available:\n"
            for offer in analysis['alternative_offers']:
                explanation += f"• {offer['type']}: ₹{offer['amount']:,.0f}\n"
        
        analysis['generated_explanation'] = explanation

    def _generate_alternative_offers(self, application_data, analysis):
        """Generate alternative loan products based on profile"""
        monthly_salary = application_data.get('monthly_salary', 0)
        cibil_score = application_data.get('cibil_score', 0)
        
        # Credit builder loan for lower scores
        if cibil_score < 700 and monthly_salary > 40000:
            analysis['alternative_offers'].append({
                'type': 'Credit Builder Loan',
                'amount': 50000,
                'tenure': '12 months',
                'interest_rate': '12%',
                'purpose': 'Build credit history',
                'features': ['Low amount', 'Short tenure', 'Credit reporting']
            })
        
        # Top-up loan for existing customers with good history
        if cibil_score > 750 and monthly_salary > 80000:
            analysis['alternative_offers'].append({
                'type': 'Preferred Customer Loan',
                'amount': min(2000000, monthly_salary * 24),
                'tenure': '84 months',
                'interest_rate': '7.5%',
                'features': ['Lower interest', 'Longer tenure', 'Flexible repayment']
            })

    def _calculate_financial_health_score(self, application_data, analysis):
        """Calculate overall financial health score (0-100)"""
        score = 50  # Base score
        
        # CIBIL Score contribution (0-30 points)
        cibil_score = application_data.get('cibil_score', 0)
        if cibil_score >= 800:
            score += 30
        elif cibil_score >= 750:
            score += 20
        elif cibil_score >= 700:
            score += 10
        elif cibil_score < 600:
            score -= 20
        
        # Income stability (0-20 points)
        monthly_salary = application_data.get('monthly_salary', 0)
        if monthly_salary >= 100000:
            score += 20
        elif monthly_salary >= 50000:
            score += 15
        elif monthly_salary >= 30000:
            score += 10
        else:
            score -= 10
        
        # Debt-to-Income ratio (0-15 points)
        existing_emi = application_data.get('existing_emi', 0)
        if monthly_salary > 0:
            dti_ratio = existing_emi / monthly_salary
            if dti_ratio < 0.2:
                score += 15
            elif dti_ratio < 0.4:
                score += 10
            elif dti_ratio > 0.6:
                score -= 15
        
        # Loan-to-Value ratio (0-15 points)
        loan_amount = application_data.get('loan_amount', 0)
        property_valuation = application_data.get('property_valuation', 0)
        if property_valuation > 0:
            ltv_ratio = loan_amount / property_valuation
            if ltv_ratio < 0.6:
                score += 15
            elif ltv_ratio < 0.8:
                score += 10
            elif ltv_ratio > 0.9:
                score -= 10
        
        # Property type bonus (0-10 points)
        if application_data.get('is_non_agricultural'):
            score += 10
        
        # Residence stability (0-10 points)
        if not application_data.get('is_rented'):
            score += 10
        
        analysis['financial_health_score'] = max(0, min(100, int(score)))

    def _determine_final_status(self, analysis):
        """Determine final application status based on analysis"""
        rejection_reasons = analysis['rejection_reasons']
        
        # Check for critical rejection reasons
        critical_reasons = [r for r in rejection_reasons if r['severity'] == 'Critical']
        high_reasons = [r for r in rejection_reasons if r['severity'] == 'High']
        
        if critical_reasons:
            analysis['status'] = 'REJECTED'
            analysis['risk_level'] = 'VERY_HIGH'
        elif high_reasons:
            analysis['status'] = 'REJECTED'
            analysis['risk_level'] = 'HIGH'
        elif rejection_reasons:
            analysis['status'] = 'UNDER_REVIEW'
            analysis['risk_level'] = 'MEDIUM'
        else:
            analysis['status'] = 'APPROVED'
            analysis['risk_level'] = 'LOW'

    def generate_detailed_report(self, application_data):
        """Generate a comprehensive PDF-ready report"""
        analysis = self.analyze_application(application_data)
        
        report = {
            'application_summary': {
                'applicant_name': f"{application_data.get('first_name', '')} {application_data.get('last_name', '')}",
                'applied_amount': application_data.get('loan_amount'),
                'property_value': application_data.get('property_valuation'),
                'application_date': datetime.now().strftime('%Y-%m-%d')
            },
            'risk_assessment': {
                'financial_health_score': analysis['financial_health_score'],
                'risk_level': analysis['risk_level'],
                'status': analysis['status']
            },
            'key_findings': {
                'strengths': [],
                'concerns': [reason['description'] for reason in analysis['rejection_reasons']],
                'opportunities': [offer['type'] for offer in analysis['alternative_offers']]
            },
            'detailed_analysis': analysis
        }
        
        return report