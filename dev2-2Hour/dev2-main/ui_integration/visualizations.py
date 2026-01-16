"""
Chart Visualization Module (logic_designer Compliant)
Plotly-based high-resolution visualization components with class-based design.
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import streamlit as st
from typing import Dict, List, Optional, Any, Tuple


class ChartTheme:
    """Chart theme management class (logic_designer compliant)"""
    
    def __init__(self):
        """Initialize theme"""
        self.colors = {
            "high": "#22c55e",
            "medium": "#f59e0b",
            "low": "#ef4444",
            "primary": "#3b82f6",
            "secondary": "#8b5cf6",
            "success": "#22c55e",
            "warning": "#f59e0b",
            "danger": "#ef4444"
        }
        self.font_sizes = {
            "title": 20,
            "label": 14,
            "number": 40,
            "small": 12
        }
        self.gauge_steps = [
            {'range': [0, 50], 'color': '#fee2e2'},
            {'range': [50, 70], 'color': '#fef3c7'},
            {'range': [70, 100], 'color': '#dcfce7'}
        ]
        self.rating_colors = ['#ef4444', '#f59e0b', '#eab308', '#84cc16', '#22c55e']
    
    def get_color_by_score(self, score: float) -> str:
        """
        Get color based on score
        
        Args:
            score: Score value (0-100)
            
        Returns:
            str: Color hex code
        """
        if score >= 70:
            return self.colors["high"]
        elif score >= 50:
            return self.colors["medium"]
        else:
            return self.colors["low"]
    
    def get_font_size(self, size_type: str) -> int:
        """
        Get font size by type
        
        Args:
            size_type: Font size type ("title", "label", "number", "small")
            
        Returns:
            int: Font size
        """
        return self.font_sizes.get(size_type, 14)


class ChartRenderer:
    """Chart rendering class (logic_designer compliant)"""
    
    def __init__(self, theme: Optional[ChartTheme] = None):
        """
        Initialize chart renderer
        
        Args:
            theme: Chart theme (None for default theme)
        """
        self.theme = theme or ChartTheme()
    
    def render_gauge_chart(
        self, 
        score: float, 
        title: str = "Reliability Score",
        min_value: float = 0.0,
        max_value: float = 100.0
    ) -> go.Figure:
        """
        Render reliability gauge chart (safe mode)
        
        Args:
            score: Reliability score (0-100)
            title: Chart title
            min_value: Minimum value (default: 0.0)
            max_value: Maximum value (default: 100.0)
            
        Returns:
            go.Figure: Plotly figure object
        """
        try:
            # Validate score
            score = max(min_value, min(max_value, score))
            color = self.theme.get_color_by_score(score)
            
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=score,
                title={'text': title, 'font': {'size': self.theme.get_font_size("title")}},
                number={'font': {'size': self.theme.get_font_size("number"), 'color': color}},
                gauge={
                    'axis': {'range': [min_value, max_value]},
                    'bar': {'color': color},
                    'steps': self.theme.gauge_steps,
                }
            ))
            fig.update_layout(
                height=350, 
                margin=dict(l=30, r=30, t=50, b=20), 
                paper_bgcolor="rgba(0,0,0,0)"
            )
            return fig
        except Exception:
            # Return empty chart on error (error-free)
            return self._empty_chart("Error rendering gauge chart")
    
    def render_radar_chart(self, products_data: List[Dict]) -> go.Figure:
        """
        Render multi-dimensional comparison radar chart (safe mode)
        
        Args:
            products_data: List of product data dictionaries
            
        Returns:
            go.Figure: Plotly figure object
        """
        try:
            if not products_data:
                return self._empty_chart("No product data available")
            
            fig = go.Figure()
            categories = ['Reliability', 'Repurchase Rate', 'Long-term Use', 'Avg Rating', 'Review Diversity']
            colors = [
                self.theme.colors["primary"],
                self.theme.colors["success"],
                self.theme.colors["warning"],
                self.theme.colors["danger"],
                self.theme.colors["secondary"]
            ]
            
            for idx, data in enumerate(products_data):
                try:
                    p = data.get("product", {})
                    ai = data.get("ai_result", {})
                    r = data.get("reviews", [])
                    
                    # Normalize metrics (0-100)
                    vals = [
                        ai.get('trust_score', 0),
                        (sum(1 for x in r if x.get("reorder", False)) / len(r) * 100) if r else 0,
                        (sum(1 for x in r if x.get("one_month_use", False)) / len(r) * 100) if r else 0,
                        (sum(x.get("rating", 5) for x in r) / len(r) * 20) if r else 0,
                        (len(set(x.get("reviewer", "") for x in r)) / len(r) * 100) if r else 0
                    ]
                    
                    brand_name = p.get('brand', f'Product {idx+1}')
                    fig.add_trace(go.Scatterpolar(
                        r=vals, 
                        theta=categories, 
                        fill='toself', 
                        name=brand_name,
                        line=dict(color=colors[idx % len(colors)], width=3)
                    ))
                except Exception:
                    # Skip individual product on error
                    continue
            
            if len(fig.data) == 0:
                return self._empty_chart("No valid product data")
            
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                height=550,
                legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center"),
                margin=dict(l=80, r=80, t=40, b=80),
                font=dict(size=self.theme.get_font_size("label"))
            )
            return fig
        except Exception:
            # Return empty chart on error (error-free)
            return self._empty_chart("Error rendering radar chart")
    
    def render_price_comparison_chart(self, products_data: List[Dict]) -> go.Figure:
        """
        Render price comparison chart (safe mode)
        
        Args:
            products_data: List of product data dictionaries
            
        Returns:
            go.Figure: Plotly figure object
        """
        try:
            if not products_data:
                return self._empty_chart("No product data available")
            
            names = []
            prices = []
            scores = []
            
            for data in products_data:
                try:
                    product = data.get("product", {})
                    ai_result = data.get("ai_result", {})
                    names.append(product.get('brand', 'Unknown'))
                    prices.append(product.get('price', 0))
                    scores.append(ai_result.get('trust_score', 0))
                except Exception:
                    # Skip individual product on error
                    continue
            
            if not names:
                return self._empty_chart("No valid product data")
            
            colors = [self.theme.get_color_by_score(s) for s in scores]
            
            fig = go.Figure(go.Bar(
                x=names, 
                y=prices, 
                marker_color=colors, 
                text=[f"${p:.2f}" for p in prices], 
                textposition='auto'
            ))
            fig.update_layout(
                title="Price Comparison by Product (USD)", 
                height=450, 
                margin=dict(t=60, b=40),
                xaxis_title="Brand",
                yaxis_title="Price (USD)"
            )
            return fig
        except Exception:
            # Return empty chart on error (error-free)
            return self._empty_chart("Error rendering price comparison chart")
    
    def render_review_sentiment_chart(self, reviews: List[Dict]) -> go.Figure:
        """
        Render review sentiment chart (rating distribution) (safe mode)
        
        Args:
            reviews: List of review dictionaries
            
        Returns:
            go.Figure: Plotly figure object
        """
        try:
            if not reviews:
                return self._empty_chart("No review data available")
            
            # Calculate rating distribution
            rating_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
            for review in reviews:
                try:
                    rating = review.get("rating", 5)
                    if rating in rating_counts:
                        rating_counts[rating] += 1
                except Exception:
                    # Skip individual review on error
                    continue
            
            # Create chart
            fig = go.Figure(data=[
                go.Bar(
                    x=list(rating_counts.keys()),
                    y=list(rating_counts.values()),
                    marker_color=self.theme.rating_colors,
                    text=[f"{count}" for count in rating_counts.values()],
                    textposition='auto',
                    name="Review Count"
                )
            ])
            
            fig.update_layout(
                title="Rating Distribution",
                xaxis_title="Rating",
                yaxis_title="Review Count",
                height=400,
                showlegend=False,
                margin=dict(t=50, b=40, l=50, r=50)
            )
            
            return fig
        except Exception:
            # Return empty chart on error (error-free)
            return self._empty_chart("Error rendering review sentiment chart")
    
    def _empty_chart(self, message: str = "No data available") -> go.Figure:
        """
        Create empty chart with message (error handling)
        
        Args:
            message: Message to display
            
        Returns:
            go.Figure: Empty plotly figure
        """
        fig = go.Figure()
        fig.add_annotation(
            text=message, 
            xref="paper", 
            yref="paper", 
            x=0.5, 
            y=0.5, 
            showarrow=False,
            font=dict(size=16)
        )
        fig.update_layout(height=300, paper_bgcolor="rgba(0,0,0,0)")
        return fig


class ChecklistVisualizer:
    """8-step checklist visualization class (logic_designer compliant)"""
    
    def __init__(self, checklist_results: Dict):
        """
        Initialize checklist visualizer
        
        Args:
            checklist_results: Checklist results dictionary
        """
        self.checklist_results = checklist_results
        self.items = {
            "1_verified_purchase": "Verified Purchase",
            "2_reorder_rate": "Repurchase Rate",
            "3_long_term_use": "Long-term Use",
            "4_rating_distribution": "Rating Distribution",
            "5_review_length": "Review Length",
            "6_time_distribution": "Time Distribution",
            "7_ad_detection": "Ad Detection",
            "8_reviewer_diversity": "Reviewer Diversity"
        }
        self.theme = ChartTheme()
    
    def render(self) -> None:
        """
        Render checklist visualization (safe mode)
        
        Returns:
            None (renders to Streamlit)
        """
        try:
            if not self.checklist_results:
                st.warning("Checklist data not available")
                return
            
            for key, label in self.items.items():
                if key in self.checklist_results:
                    try:
                        self._render_item(key, label, self.checklist_results[key])
                    except Exception:
                        # Skip individual item on error
                        continue
        except Exception:
            st.error("Error rendering checklist visualization")
    
    def _render_item(self, key: str, label: str, result: Dict) -> None:
        """
        Render individual checklist item
        
        Args:
            key: Checklist item key
            label: Checklist item label
            result: Checklist item result dictionary
        """
        passed = result.get("passed", False)
        rate = result.get("rate", 0)
        
        status_icon = "✅" if passed else "❌"
        status_color = self.theme.colors["success"] if passed else self.theme.colors["danger"]
        
        st.markdown(f"{status_icon} **{label}**")
        st.progress(rate, text=f"{rate*100:.1f}%")


class ComparisonTableRenderer:
    """Product comparison table renderer class (logic_designer compliant)"""
    
    def __init__(self, products_data: List[Dict]):
        """
        Initialize comparison table renderer
        
        Args:
            products_data: List of product data dictionaries
        """
        self.products_data = products_data
    
    def render(self) -> pd.DataFrame:
        """
        Render comparison table (safe mode)
        
        Returns:
            pd.DataFrame: Comparison table DataFrame
        """
        try:
            if not self.products_data:
                return pd.DataFrame()
            
            table_data = []
            
            for data in self.products_data:
                try:
                    row = self._calculate_row(data)
                    if row:
                        table_data.append(row)
                except Exception:
                    # Skip individual product on error
                    continue
            
            if not table_data:
                return pd.DataFrame()
            
            return pd.DataFrame(table_data)
        except Exception:
            # Return empty DataFrame on error (error-free)
            return pd.DataFrame()
    
    def _calculate_row(self, data: Dict) -> Optional[Dict]:
        """
        Calculate row data for a product
        
        Args:
            data: Product data dictionary
            
        Returns:
            Optional[Dict]: Row data dictionary or None
        """
        try:
            product = data.get("product", {})
            ai_result = data.get("ai_result", {})
            reviews = data.get("reviews", [])
            
            # Calculate statistics
            total_reviews = len(reviews)
            if total_reviews == 0:
                return None
            
            verified_count = sum(1 for r in reviews if r.get("verified", False))
            reorder_count = sum(1 for r in reviews if r.get("reorder", False))
            one_month_count = sum(1 for r in reviews if r.get("one_month_use", False))
            avg_rating = sum(r.get("rating", 5) for r in reviews) / total_reviews
            
            # Advertising suspicion rate
            ad_suspected = sum(
                1 for r in reviews
                if r.get("rating") == 5 and not r.get("one_month_use") and len(r.get("text", "")) < 100
            )
            ad_rate = (ad_suspected / total_reviews * 100) if total_reviews > 0 else 0
            
            return {
                "Product": f"{product.get('brand', '')} {product.get('name', '')}",
                "Reliability": f"{ai_result.get('trust_score', 0):.1f}",
                "Grade": ai_result.get('trust_level', 'medium').upper(),
                "Price ($)": f"{product.get('price', 0):.2f}",
                "Reviews": f"{total_reviews}",
                "Avg Rating": f"{avg_rating:.1f}/5",
                "Verified": f"{verified_count/total_reviews*100:.1f}%",
                "Repurchase": f"{reorder_count/total_reviews*100:.1f}%",
                "1 Month+": f"{one_month_count/total_reviews*100:.1f}%",
                "Ad Suspicion": f"{ad_rate:.1f}%"
            }
        except Exception:
            return None


class TrustBadgeRenderer:
    """Trust badge renderer class (logic_designer compliant)"""
    
    def __init__(self, theme: Optional[ChartTheme] = None):
        """
        Initialize trust badge renderer
        
        Args:
            theme: Chart theme (None for default theme)
        """
        self.theme = theme or ChartTheme()
    
    def render(self, level: str) -> str:
        """
        Render trust badge HTML (safe mode)
        
        Args:
            level: Trust level ("high", "medium", "low")
            
        Returns:
            str: HTML string for badge
        """
        try:
            level = level.lower()
            if level == "high":
                color = self.theme.colors["high"]
                text = "HIGH"
            elif level == "medium":
                color = self.theme.colors["medium"]
                text = "MEDIUM"
            else:
                color = self.theme.colors["low"]
                text = "LOW"
            
            return f'<div style="background: {color}; color: white; padding: 8px 16px; border-radius: 20px; display: inline-block; font-weight: bold; font-size: 0.9rem;">{text}</div>'
        except Exception:
            # Return default badge on error (error-free)
            return '<div style="background: #6b7280; color: white; padding: 8px 16px; border-radius: 20px; display: inline-block; font-weight: bold; font-size: 0.9rem;">UNKNOWN</div>'


# ========== Convenience Functions (Backward Compatibility) ==========

# Singleton instances
_default_theme = ChartTheme()
_default_renderer = ChartRenderer(_default_theme)
_default_badge_renderer = TrustBadgeRenderer(_default_theme)


def render_gauge_chart(score: float, title: str = "Reliability Score") -> go.Figure:
    """
    Render reliability gauge chart (convenience function)
    
    Args:
        score: Reliability score (0-100)
        title: Chart title
        
    Returns:
        go.Figure: Plotly figure object
    """
    return _default_renderer.render_gauge_chart(score, title)


def render_radar_chart(products_data: List[Dict]) -> go.Figure:
    """
    Render multi-dimensional comparison radar chart (convenience function)
    
    Args:
        products_data: List of product data dictionaries
        
    Returns:
        go.Figure: Plotly figure object
    """
    return _default_renderer.render_radar_chart(products_data)


def render_price_comparison_chart(products_data: List[Dict]) -> go.Figure:
    """
    Render price comparison chart (convenience function)
    
    Args:
        products_data: List of product data dictionaries
        
    Returns:
        go.Figure: Plotly figure object
    """
    return _default_renderer.render_price_comparison_chart(products_data)


def render_review_sentiment_chart(reviews: List[Dict]) -> go.Figure:
    """
    Render review sentiment chart (convenience function)
    
    Args:
        reviews: List of review dictionaries
        
    Returns:
        go.Figure: Plotly figure object
    """
    return _default_renderer.render_review_sentiment_chart(reviews)


def render_trust_badge(level: str) -> str:
    """
    Render trust badge HTML (convenience function)
    
    Args:
        level: Trust level ("high", "medium", "low")
        
    Returns:
        str: HTML string for badge
    """
    return _default_badge_renderer.render(level)


def render_comparison_table(products_data: List[Dict]) -> pd.DataFrame:
    """
    Render comparison table (convenience function)
    
    Args:
        products_data: List of product data dictionaries
        
    Returns:
        pd.DataFrame: Comparison table DataFrame
    """
    renderer = ComparisonTableRenderer(products_data)
    return renderer.render()


def render_checklist_visual(checklist_results: Dict) -> None:
    """
    Render checklist visualization (convenience function)
    
    Args:
        checklist_results: Checklist results dictionary
        
    Returns:
        None (renders to Streamlit)
    """
    visualizer = ChecklistVisualizer(checklist_results)
    visualizer.render()
