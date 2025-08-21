"""
Enhanced Automated Reporting Service with AI Narrative Generation
This service provides comprehensive report generation capabilities including
AI-powered narrative creation, data visualization, and PDF export.
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import asyncio
import logging
from pathlib import Path
import base64
import io

# For PDF generation and chart creation
try:
    import matplotlib
    matplotlib.use('Agg')  # Use non-GUI backend
    import matplotlib.pyplot as plt
    import seaborn as sns
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    REPORTING_DEPENDENCIES = True
except ImportError:
    REPORTING_DEPENDENCIES = False
    logging.warning("Reporting dependencies not installed. Install with: pip install matplotlib seaborn reportlab")

logger = logging.getLogger(__name__)

class AIReportingService:
    """
    AI-Enhanced Reporting Service for DataRW Projects
    Generates comprehensive reports with AI narratives, visualizations, and PDF exports
    """
    
    def __init__(self, db):
        self.db = db
        self.reports_dir = Path("/app/generated_reports")
        self.reports_dir.mkdir(exist_ok=True)
        
        # Chart styling
        if REPORTING_DEPENDENCIES:
            plt.style.use('seaborn-v0_8')
            sns.set_palette("husl")
    
    async def generate_project_report(
        self, 
        project_id: str, 
        report_type: str, 
        period_start: datetime, 
        period_end: datetime,
        include_images: bool = True,
        ai_narrative: bool = True
    ) -> Dict[str, Any]:
        """
        Generate comprehensive project report with AI narrative
        """
        try:
            logger.info(f"Generating {report_type} report for project {project_id}")
            
            # Gather project data
            project_data = await self._collect_project_data(project_id, period_start, period_end)
            
            if not project_data:
                raise Exception(f"No data found for project {project_id}")
            
            # Generate AI narrative
            narrative = ""
            if ai_narrative:
                narrative = await self._generate_ai_narrative(project_data, report_type, period_start, period_end)
            
            # Create visualizations
            charts = []
            if include_images:
                charts = await self._generate_visualizations(project_data, project_id)
            
            # Generate report document
            report_id = str(uuid.uuid4())
            pdf_path = await self._generate_pdf_report(
                report_id, 
                project_data, 
                narrative, 
                charts, 
                report_type,
                period_start,
                period_end
            )
            
            # Save report metadata
            report_metadata = {
                "id": report_id,
                "project_id": project_id,
                "report_type": report_type,
                "period_start": period_start,
                "period_end": period_end,
                "generated_at": datetime.utcnow(),
                "pdf_path": str(pdf_path),
                "narrative_length": len(narrative),
                "charts_count": len(charts),
                "status": "completed"
            }
            
            await self.db.generated_reports.insert_one(report_metadata)
            
            return {
                "success": True,
                "report_id": report_id,
                "pdf_path": str(pdf_path),
                "narrative": narrative,
                "charts": charts,
                "metadata": report_metadata
            }
            
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _collect_project_data(self, project_id: str, period_start: datetime, period_end: datetime) -> Dict[str, Any]:
        """
        Collect comprehensive project data for report generation
        """
        try:
            # Get project details
            project = await self.db.projects.find_one({"id": project_id})
            if not project:
                return None
            
            # Get activities
            activities = []
            async for activity in self.db.activities.find({"project_id": project_id}):
                activities.append(activity)
            
            # Get budget items
            budget_items = []
            async for budget in self.db.budget_items.find({"project_id": project_id}):
                budget_items.append(budget)
            
            # Get KPIs
            kpis = []
            async for kpi in self.db.kpi_indicators.find({"project_id": project_id}):
                kpis.append(kpi)
            
            # Get beneficiaries
            beneficiaries = []
            async for beneficiary in self.db.beneficiaries.find({"project_id": project_id}):
                beneficiaries.append(beneficiary)
            
            # Calculate summary statistics
            total_budget = sum(item.get("budgeted_amount", 0) for item in budget_items)
            utilized_budget = sum(item.get("utilized_amount", 0) for item in budget_items)
            budget_utilization = (utilized_budget / total_budget * 100) if total_budget > 0 else 0
            
            completed_activities = len([a for a in activities if a.get("status") == "completed"])
            total_activities = len(activities)
            activity_completion = (completed_activities / total_activities * 100) if total_activities > 0 else 0
            
            kpi_achievement = 0
            if kpis:
                achieved_kpis = sum(1 for kpi in kpis if kpi.get("achievement_percentage", 0) >= 100)
                kpi_achievement = (achieved_kpis / len(kpis) * 100)
            
            return {
                "project": project,
                "activities": activities,
                "budget_items": budget_items,
                "kpis": kpis,
                "beneficiaries": beneficiaries,
                "summary": {
                    "total_budget": total_budget,
                    "utilized_budget": utilized_budget,
                    "budget_utilization": budget_utilization,
                    "total_activities": total_activities,
                    "completed_activities": completed_activities,
                    "activity_completion": activity_completion,
                    "total_beneficiaries": len(beneficiaries),
                    "kpi_achievement": kpi_achievement,
                    "period_start": period_start,
                    "period_end": period_end
                }
            }
            
        except Exception as e:
            logger.error(f"Error collecting project data: {str(e)}")
            return None
    
    async def _generate_ai_narrative(
        self, 
        project_data: Dict[str, Any], 
        report_type: str, 
        period_start: datetime, 
        period_end: datetime
    ) -> str:
        """
        Generate AI-powered narrative for the report
        """
        try:
            # Use emergentintegrations for AI generation
            from emergentintegrations import LLMIntegration
            
            llm = LLMIntegration()
            
            project = project_data["project"]
            summary = project_data["summary"]
            
            # Create comprehensive prompt for AI narrative
            prompt = f"""
            Generate a comprehensive, professional project report narrative for the following project:
            
            **Project Information:**
            - Project Name: {project.get("name", "Unknown")}
            - Description: {project.get("description", "No description available")}
            - Project Manager: {project.get("project_manager_id", "Not specified")}
            - Period: {period_start.strftime("%B %Y")} to {period_end.strftime("%B %Y")}
            - Report Type: {report_type}
            
            **Performance Summary:**
            - Total Budget: {summary["total_budget"]:,.0f} RWF
            - Budget Utilized: {summary["utilized_budget"]:,.0f} RWF ({summary["budget_utilization"]:.1f}%)
            - Activities Completed: {summary["completed_activities"]}/{summary["total_activities"]} ({summary["activity_completion"]:.1f}%)
            - Beneficiaries Reached: {summary["total_beneficiaries"]}
            - KPI Achievement: {summary["kpi_achievement"]:.1f}%
            
            **Activities Overview:**
            {self._format_activities_for_prompt(project_data["activities"])}
            
            **Budget Breakdown:**
            {self._format_budget_for_prompt(project_data["budget_items"])}
            
            **KPI Performance:**
            {self._format_kpis_for_prompt(project_data["kpis"])}
            
            Please generate a comprehensive narrative report that includes:
            1. Executive Summary (2-3 paragraphs)
            2. Project Progress Analysis (3-4 paragraphs)
            3. Financial Performance Review (2-3 paragraphs)
            4. Key Achievements and Milestones (2-3 paragraphs)
            5. Challenges and Risk Assessment (2-3 paragraphs)
            6. Beneficiary Impact Analysis (2-3 paragraphs)
            7. Recommendations and Next Steps (2-3 paragraphs)
            
            Use professional language suitable for stakeholders, donors, and project management. 
            Include specific data points and percentages where relevant.
            Focus on insights, trends, and actionable recommendations.
            """
            
            # Generate narrative using emergent AI
            response = await llm.generate_text(
                prompt=prompt,
                max_tokens=2500,
                temperature=0.7
            )
            
            return response.get("text", "AI narrative generation unavailable at this time.")
            
        except Exception as e:
            logger.error(f"Error generating AI narrative: {str(e)}")
            # Fallback to basic narrative
            return self._generate_basic_narrative(project_data, report_type, period_start, period_end)
    
    def _generate_basic_narrative(
        self, 
        project_data: Dict[str, Any], 
        report_type: str, 
        period_start: datetime, 
        period_end: datetime
    ) -> str:
        """
        Generate basic narrative without AI (fallback)
        """
        project = project_data["project"]
        summary = project_data["summary"]
        
        narrative = f"""
        # {report_type} Report: {project.get("name", "Project Report")}
        
        ## Executive Summary
        
        This {report_type.lower()} report covers the period from {period_start.strftime("%B %d, %Y")} to {period_end.strftime("%B %d, %Y")}. 
        The project has achieved {summary["activity_completion"]:.1f}% completion of planned activities and {summary["budget_utilization"]:.1f}% budget utilization.
        
        ## Project Progress
        
        During this reporting period, the project completed {summary["completed_activities"]} out of {summary["total_activities"]} planned activities. 
        The project has reached {summary["total_beneficiaries"]} beneficiaries and achieved {summary["kpi_achievement"]:.1f}% of its KPI targets.
        
        ## Financial Performance
        
        Total project budget allocation stands at {summary["total_budget"]:,.0f} RWF, with {summary["utilized_budget"]:,.0f} RWF utilized to date. 
        This represents a budget utilization rate of {summary["budget_utilization"]:.1f}%, indicating {"efficient" if summary["budget_utilization"] < 95 else "high"} resource management.
        
        ## Key Achievements
        
        The project has made significant progress in meeting its objectives, with notable achievements in activity implementation and beneficiary engagement.
        
        ## Recommendations
        
        Based on current progress, the project is {"on track" if summary["activity_completion"] > 75 else "requiring attention"} to meet its planned objectives. 
        Continued focus on activity completion and budget management will be essential for project success.
        """
        
        return narrative
    
    def _format_activities_for_prompt(self, activities: List[Dict]) -> str:
        """Format activities data for AI prompt"""
        if not activities:
            return "No activities data available."
        
        formatted = []
        for activity in activities[:5]:  # Limit to top 5 for prompt size
            status = activity.get("status", "unknown")
            progress = activity.get("progress_percentage", 0)
            formatted.append(f"- {activity.get('name', 'Unnamed Activity')}: {status.title()} ({progress:.0f}% complete)")
        
        return "\n".join(formatted)
    
    def _format_budget_for_prompt(self, budget_items: List[Dict]) -> str:
        """Format budget data for AI prompt"""
        if not budget_items:
            return "No budget data available."
        
        categories = {}
        for item in budget_items:
            category = item.get("category", "other")
            if category not in categories:
                categories[category] = {"budgeted": 0, "utilized": 0}
            categories[category]["budgeted"] += item.get("budgeted_amount", 0)
            categories[category]["utilized"] += item.get("utilized_amount", 0)
        
        formatted = []
        for category, amounts in categories.items():
            utilization = (amounts["utilized"] / amounts["budgeted"] * 100) if amounts["budgeted"] > 0 else 0
            formatted.append(f"- {category.title()}: {amounts['utilized']:,.0f}/{amounts['budgeted']:,.0f} RWF ({utilization:.1f}%)")
        
        return "\n".join(formatted)
    
    def _format_kpis_for_prompt(self, kpis: List[Dict]) -> str:
        """Format KPIs data for AI prompt"""
        if not kpis:
            return "No KPIs data available."
        
        formatted = []
        for kpi in kpis[:5]:  # Limit to top 5
            achievement = kpi.get("achievement_percentage", 0)
            target = kpi.get("target_value", "N/A")
            current = kpi.get("current_value", "N/A")
            formatted.append(f"- {kpi.get('name', 'Unnamed KPI')}: {current}/{target} ({achievement:.1f}% achieved)")
        
        return "\n".join(formatted)
    
    async def _generate_visualizations(self, project_data: Dict[str, Any], project_id: str) -> List[Dict[str, Any]]:
        """
        Generate data visualizations for the report
        """
        if not REPORTING_DEPENDENCIES:
            logger.warning("Reporting dependencies not available. Skipping visualizations.")
            return []
        
        charts = []
        chart_dir = self.reports_dir / f"charts_{project_id}"
        chart_dir.mkdir(exist_ok=True)
        
        try:
            # 1. Budget Utilization Chart
            budget_chart = await self._create_budget_chart(project_data["budget_items"], chart_dir)
            if budget_chart:
                charts.append(budget_chart)
            
            # 2. Activity Progress Chart
            activity_chart = await self._create_activity_chart(project_data["activities"], chart_dir)
            if activity_chart:
                charts.append(activity_chart)
            
            # 3. KPI Achievement Chart
            kpi_chart = await self._create_kpi_chart(project_data["kpis"], chart_dir)
            if kpi_chart:
                charts.append(kpi_chart)
            
            # 4. Beneficiary Demographics Chart
            beneficiary_chart = await self._create_beneficiary_chart(project_data["beneficiaries"], chart_dir)
            if beneficiary_chart:
                charts.append(beneficiary_chart)
            
            # 5. Monthly Progress Trend (if enough data)
            trend_chart = await self._create_trend_chart(project_data, chart_dir)
            if trend_chart:
                charts.append(trend_chart)
            
            return charts
            
        except Exception as e:
            logger.error(f"Error generating visualizations: {str(e)}")
            return []
    
    async def _create_budget_chart(self, budget_items: List[Dict], chart_dir: Path) -> Optional[Dict[str, Any]]:
        """Create budget utilization chart"""
        try:
            if not budget_items:
                return None
            
            # Group by category
            categories = {}
            for item in budget_items:
                category = item.get("category", "other")
                if category not in categories:
                    categories[category] = {"budgeted": 0, "utilized": 0}
                categories[category]["budgeted"] += item.get("budgeted_amount", 0)
                categories[category]["utilized"] += item.get("utilized_amount", 0)
            
            if not categories:
                return None
            
            # Create chart
            fig, ax = plt.subplots(figsize=(10, 6))
            
            category_names = list(categories.keys())
            budgeted_amounts = [categories[cat]["budgeted"] for cat in category_names]
            utilized_amounts = [categories[cat]["utilized"] for cat in category_names]
            
            x = range(len(category_names))
            width = 0.35
            
            ax.bar([i - width/2 for i in x], budgeted_amounts, width, label='Budgeted', color='#3B82F6')
            ax.bar([i + width/2 for i in x], utilized_amounts, width, label='Utilized', color='#10B981')
            
            ax.set_xlabel('Budget Categories')
            ax.set_ylabel('Amount (RWF)')
            ax.set_title('Budget Utilization by Category')
            ax.set_xticks(x)
            ax.set_xticklabels([cat.title() for cat in category_names], rotation=45)
            ax.legend()
            
            plt.tight_layout()
            
            chart_path = chart_dir / "budget_utilization.png"
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return {
                "title": "Budget Utilization by Category",
                "path": str(chart_path),
                "type": "bar_chart",
                "description": "Comparison of budgeted vs utilized amounts by category"
            }
            
        except Exception as e:
            logger.error(f"Error creating budget chart: {str(e)}")
            return None
    
    async def _create_activity_chart(self, activities: List[Dict], chart_dir: Path) -> Optional[Dict[str, Any]]:
        """Create activity progress chart"""
        try:
            if not activities:
                return None
            
            # Count activities by status
            status_counts = {}
            for activity in activities:
                status = activity.get("status", "not_started")
                status_counts[status] = status_counts.get(status, 0) + 1
            
            if not status_counts:
                return None
            
            # Create pie chart
            fig, ax = plt.subplots(figsize=(8, 8))
            
            labels = [status.replace("_", " ").title() for status in status_counts.keys()]
            sizes = list(status_counts.values())
            colors = ['#10B981', '#3B82F6', '#F59E0B', '#EF4444', '#8B5CF6']
            
            ax.pie(sizes, labels=labels, colors=colors[:len(labels)], autopct='%1.1f%%', startangle=90)
            ax.set_title('Activity Status Distribution')
            
            plt.tight_layout()
            
            chart_path = chart_dir / "activity_status.png"
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return {
                "title": "Activity Status Distribution",
                "path": str(chart_path),
                "type": "pie_chart",
                "description": "Distribution of activities by completion status"
            }
            
        except Exception as e:
            logger.error(f"Error creating activity chart: {str(e)}")
            return None
    
    async def _create_kpi_chart(self, kpis: List[Dict], chart_dir: Path) -> Optional[Dict[str, Any]]:
        """Create KPI achievement chart"""
        try:
            if not kpis:
                return None
            
            # Get KPI achievements
            kpi_names = []
            achievements = []
            
            for kpi in kpis[:8]:  # Limit to 8 KPIs for readability
                name = kpi.get("name", "Unnamed KPI")
                achievement = kpi.get("achievement_percentage", 0)
                kpi_names.append(name[:30] + "..." if len(name) > 30 else name)
                achievements.append(achievement)
            
            if not kpi_names:
                return None
            
            # Create horizontal bar chart
            fig, ax = plt.subplots(figsize=(12, 8))
            
            bars = ax.barh(kpi_names, achievements)
            
            # Color bars based on achievement
            for i, bar in enumerate(bars):
                if achievements[i] >= 100:
                    bar.set_color('#10B981')  # Green for achieved
                elif achievements[i] >= 75:
                    bar.set_color('#F59E0B')  # Yellow for near achievement
                else:
                    bar.set_color('#EF4444')  # Red for behind target
            
            ax.set_xlabel('Achievement Percentage (%)')
            ax.set_title('KPI Achievement Status')
            ax.axvline(x=100, color='gray', linestyle='--', alpha=0.7)
            
            plt.tight_layout()
            
            chart_path = chart_dir / "kpi_achievement.png"
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return {
                "title": "KPI Achievement Status",
                "path": str(chart_path),
                "type": "horizontal_bar_chart",
                "description": "Progress towards KPI targets"
            }
            
        except Exception as e:
            logger.error(f"Error creating KPI chart: {str(e)}")
            return None
    
    async def _create_beneficiary_chart(self, beneficiaries: List[Dict], chart_dir: Path) -> Optional[Dict[str, Any]]:
        """Create beneficiary demographics chart"""
        try:
            if not beneficiaries:
                return None
            
            # Analyze gender distribution
            gender_counts = {}
            for beneficiary in beneficiaries:
                gender = beneficiary.get("gender", "other")
                gender_counts[gender] = gender_counts.get(gender, 0) + 1
            
            if not gender_counts:
                return None
            
            # Create donut chart
            fig, ax = plt.subplots(figsize=(8, 8))
            
            labels = [gender.replace("_", " ").title() for gender in gender_counts.keys()]
            sizes = list(gender_counts.values())
            colors = ['#3B82F6', '#EC4899', '#10B981', '#F59E0B']
            
            wedges, texts, autotexts = ax.pie(
                sizes, 
                labels=labels, 
                colors=colors[:len(labels)], 
                autopct='%1.1f%%',
                pctdistance=0.85,
                startangle=90
            )
            
            # Create donut effect
            centre_circle = plt.Circle((0,0), 0.70, fc='white')
            ax.add_artist(centre_circle)
            
            ax.set_title('Beneficiary Gender Distribution')
            
            plt.tight_layout()
            
            chart_path = chart_dir / "beneficiary_demographics.png"
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return {
                "title": "Beneficiary Gender Distribution",
                "path": str(chart_path),
                "type": "donut_chart",
                "description": "Distribution of beneficiaries by gender"
            }
            
        except Exception as e:
            logger.error(f"Error creating beneficiary chart: {str(e)}")
            return None
    
    async def _create_trend_chart(self, project_data: Dict[str, Any], chart_dir: Path) -> Optional[Dict[str, Any]]:
        """Create monthly progress trend chart"""
        try:
            # This would require historical data - for now, create a sample trend
            fig, ax = plt.subplots(figsize=(12, 6))
            
            # Sample monthly progress data
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
            budget_progress = [10, 25, 45, 60, 75, 85]
            activity_progress = [15, 30, 50, 65, 80, 90]
            
            ax.plot(months, budget_progress, marker='o', label='Budget Utilization %', linewidth=2)
            ax.plot(months, activity_progress, marker='s', label='Activity Completion %', linewidth=2)
            
            ax.set_xlabel('Month')
            ax.set_ylabel('Progress (%)')
            ax.set_title('Project Progress Trends')
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            chart_path = chart_dir / "progress_trends.png"
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return {
                "title": "Project Progress Trends",
                "path": str(chart_path),
                "type": "line_chart",
                "description": "Monthly progress trends for budget and activities"
            }
            
        except Exception as e:
            logger.error(f"Error creating trend chart: {str(e)}")
            return None
    
    async def _generate_pdf_report(
        self,
        report_id: str,
        project_data: Dict[str, Any],
        narrative: str,
        charts: List[Dict[str, Any]],
        report_type: str,
        period_start: datetime,
        period_end: datetime
    ) -> Path:
        """
        Generate PDF report with narrative and visualizations
        """
        if not REPORTING_DEPENDENCIES:
            # Create a simple text file if PDF generation not available
            txt_path = self.reports_dir / f"report_{report_id}.txt"
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(f"Report: {report_type}\n")
                f.write(f"Project: {project_data['project'].get('name', 'Unknown')}\n")
                f.write(f"Period: {period_start} to {period_end}\n\n")
                f.write(narrative)
            return txt_path
        
        try:
            pdf_path = self.reports_dir / f"report_{report_id}.pdf"
            doc = SimpleDocTemplate(str(pdf_path), pagesize=A4)
            
            # Styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                spaceAfter=30,
                textColor=colors.darkblue,
                alignment=1  # Center alignment
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=14,
                spaceAfter=12,
                textColor=colors.darkblue
            )
            
            normal_style = ParagraphStyle(
                'CustomNormal',
                parent=styles['Normal'],
                fontSize=11,
                spaceAfter=12,
                alignment=4  # Justify
            )
            
            # Build content
            content = []
            
            # Title page
            project_name = project_data['project'].get('name', 'Project Report')
            content.append(Paragraph(f"{report_type} Report", title_style))
            content.append(Paragraph(project_name, title_style))
            content.append(Spacer(1, 20))
            content.append(Paragraph(f"Period: {period_start.strftime('%B %d, %Y')} to {period_end.strftime('%B %d, %Y')}", normal_style))
            content.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", normal_style))
            content.append(PageBreak())
            
            # Executive Summary
            summary = project_data['summary']
            content.append(Paragraph("Executive Summary", heading_style))
            summary_text = f"""
            This {report_type.lower()} report presents the performance analysis of {project_name} for the reporting period. 
            The project achieved {summary['activity_completion']:.1f}% activity completion and {summary['budget_utilization']:.1f}% budget utilization. 
            A total of {summary['total_beneficiaries']} beneficiaries were reached during this period.
            """
            content.append(Paragraph(summary_text, normal_style))
            content.append(Spacer(1, 20))
            
            # Key Metrics Table
            content.append(Paragraph("Key Performance Metrics", heading_style))
            metrics_data = [
                ['Metric', 'Value', 'Performance'],
                ['Total Budget', f"{summary['total_budget']:,.0f} RWF", ""],
                ['Budget Utilized', f"{summary['utilized_budget']:,.0f} RWF", f"{summary['budget_utilization']:.1f}%"],
                ['Activities Completed', f"{summary['completed_activities']}/{summary['total_activities']}", f"{summary['activity_completion']:.1f}%"],
                ['Beneficiaries Reached', str(summary['total_beneficiaries']), ""],
                ['KPI Achievement', f"{summary['kpi_achievement']:.1f}%", ""]
            ]
            
            metrics_table = Table(metrics_data, colWidths=[2.5*inch, 2*inch, 1.5*inch])
            metrics_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            content.append(metrics_table)
            content.append(Spacer(1, 20))
            
            # Add charts
            for chart in charts:
                try:
                    content.append(Paragraph(chart['title'], heading_style))
                    img = Image(chart['path'], width=6*inch, height=4*inch)
                    content.append(img)
                    content.append(Paragraph(chart['description'], normal_style))
                    content.append(Spacer(1, 20))
                except Exception as e:
                    logger.warning(f"Could not add chart {chart['title']}: {str(e)}")
            
            # Add narrative
            content.append(PageBreak())
            content.append(Paragraph("Detailed Analysis", heading_style))
            
            # Split narrative into paragraphs
            narrative_paragraphs = narrative.split('\n\n')
            for para in narrative_paragraphs:
                if para.strip():
                    # Handle markdown-style headers
                    if para.startswith('#'):
                        # Remove markdown and use as heading
                        header_text = para.lstrip('#').strip()
                        content.append(Paragraph(header_text, heading_style))
                    else:
                        content.append(Paragraph(para.strip(), normal_style))
            
            # Build PDF
            doc.build(content)
            
            logger.info(f"PDF report generated successfully: {pdf_path}")
            return pdf_path
            
        except Exception as e:
            logger.error(f"Error generating PDF: {str(e)}")
            # Fallback to text file
            txt_path = self.reports_dir / f"report_{report_id}.txt"
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(f"Report: {report_type}\n")
                f.write(f"Project: {project_data['project'].get('name', 'Unknown')}\n")
                f.write(f"Period: {period_start} to {period_end}\n\n")
                f.write(narrative)
            return txt_path
    
    async def get_report_templates(self) -> List[Dict[str, Any]]:
        """Get available report templates"""
        return [
            {
                "id": "monthly",
                "name": "Monthly Report",
                "description": "Comprehensive monthly progress report with KPIs and activities",
                "frequency": "monthly",
                "sections": ["executive_summary", "activities", "budget", "kpis", "beneficiaries", "recommendations"]
            },
            {
                "id": "quarterly",
                "name": "Quarterly Report", 
                "description": "Detailed quarterly review with trend analysis and strategic insights",
                "frequency": "quarterly",
                "sections": ["executive_summary", "strategic_overview", "financial_analysis", "impact_assessment", "risk_analysis", "recommendations"]
            },
            {
                "id": "annual",
                "name": "Annual Report",
                "description": "Comprehensive yearly review with full impact assessment",
                "frequency": "annual", 
                "sections": ["executive_summary", "year_overview", "impact_analysis", "financial_summary", "lessons_learned", "future_planning"]
            },
            {
                "id": "donor",
                "name": "Donor Report",
                "description": "Specialized report for donors with financial focus and impact metrics",
                "frequency": "custom",
                "sections": ["executive_summary", "financial_transparency", "impact_metrics", "beneficiary_stories", "sustainability_plan"]
            }
        ]
    
    async def get_generated_reports(self, project_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get list of generated reports"""
        try:
            query = {"project_id": project_id} if project_id else {}
            reports = []
            
            async for report in self.db.generated_reports.find(query).sort("generated_at", -1):
                reports.append({
                    "id": report["id"],
                    "project_id": report["project_id"],
                    "report_type": report["report_type"],
                    "generated_at": report["generated_at"],
                    "status": report["status"],
                    "pdf_path": report["pdf_path"],
                    "file_size": self._get_file_size(report["pdf_path"])
                })
            
            return reports
            
        except Exception as e:
            logger.error(f"Error getting generated reports: {str(e)}")
            return []
    
    def _get_file_size(self, file_path: str) -> str:
        """Get human-readable file size"""
        try:
            size = Path(file_path).stat().st_size
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024.0:
                    return f"{size:.1f} {unit}"
                size /= 1024.0
            return f"{size:.1f} TB"
        except:
            return "Unknown"