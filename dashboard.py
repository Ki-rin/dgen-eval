"""
Dashboard component for the Documentation Evaluation Streamlit app.
Contains visualization functions for evaluation metrics.
"""

import streamlit as st
import pandas as pd
import altair as alt
import os
from pathlib import Path
import numpy as np

def load_all_evaluation_results(results_dir):
    """
    Load all evaluation results from a directory and merge them.
    
    Args:
        results_dir: Directory containing evaluation CSV files
        
    Returns:
        DataFrame with all evaluation results
    """
    all_data = []
    
    if not os.path.exists(results_dir):
        return pd.DataFrame()
    
    for file in os.listdir(results_dir):
        if file.endswith("_eval.csv"):
            try:
                file_path = os.path.join(results_dir, file)
                df = pd.read_csv(file_path)
                
                # Add section number
                section_num = file.split("Section")[1].split("_")[0]
                df["Section Number"] = section_num
                
                all_data.append(df)
            except Exception as e:
                st.error(f"Error loading {file}: {e}")
    
    if all_data:
        return pd.concat(all_data, ignore_index=True)
    else:
        return pd.DataFrame()

def create_metric_chart(df, metric_name, inverted=False):
    """
    Create a bar chart for a specific metric across all sections.
    
    Args:
        df: DataFrame with evaluation results
        metric_name: Name of the metric to visualize (e.g., 'Coherence Score')
        inverted: Whether lower scores are better (for hallucination)
    
    Returns:
        Altair chart object
    """
    if df.empty or metric_name not in df.columns:
        return None
    
    # Prepare data
    chart_data = df[['Section Title', metric_name]].copy()
    chart_data = chart_data.rename(columns={metric_name: 'Score'})
    
    # Define color scale (inverted for hallucination where lower is better)
    if inverted:
        color_scale = alt.Scale(domain=[0, 0.5, 1], range=['#28a745', '#ffc107', '#dc3545'])
    else:
        color_scale = alt.Scale(domain=[0, 0.5, 1], range=['#dc3545', '#ffc107', '#28a745'])
    
    # Create chart
    chart = alt.Chart(chart_data).mark_bar().encode(
        x=alt.X('Section Title:N', sort=None, title='Section'),
        y=alt.Y('Score:Q', scale=alt.Scale(domain=[0, 1]), title='Score'),
        color=alt.Color('Score:Q', scale=color_scale),
        tooltip=['Section Title', 'Score']
    ).properties(
        title=f"{metric_name.replace(' Score', '')} Scores by Section",
        width=600,
        height=300
    )
    
    return chart

def create_overall_chart(df):
    """
    Create a radar chart for the overall metrics.
    
    Args:
        df: DataFrame with evaluation results
        
    Returns:
        Altair chart object
    """
    if df.empty:
        return None
    
    # Prepare data for radar chart (using a line chart in polar coordinates)
    metrics = ['Coherence Score', 'Quality Score', 'Capture Rate', 'Hallucination Score']
    
    # Need to invert hallucination score where lower is better
    df_avg = df.copy()
    df_avg['Hallucination Score'] = 1 - df_avg['Hallucination Score']
    
    # Calculate average scores
    avg_scores = {
        'Coherence': df_avg['Coherence Score'].mean(),
        'Quality': df_avg['Quality Score'].mean(),
        'Capture': df_avg['Capture Rate'].mean(),
        'Hallucination': df_avg['Hallucination Score'].mean()  # Already inverted
    }
    
    # Convert to format for radial chart
    radar_data = pd.DataFrame({
        'Metric': list(avg_scores.keys()),
        'Score': list(avg_scores.values())
    })
    
    # Create chart
    chart = alt.Chart(radar_data).mark_bar().encode(
        x=alt.X('Metric:N', title=None),
        y=alt.Y('Score:Q', scale=alt.Scale(domain=[0, 1])),
        color=alt.Color('Metric:N', legend=None),
        tooltip=['Metric', 'Score']
    ).properties(
        title="Average Scores Across All Sections",
        width=600,
        height=300
    )
    
    return chart

def create_section_comparison(df):
    """
    Create a heatmap comparing all sections across metrics.
    
    Args:
        df: DataFrame with evaluation results
        
    Returns:
        Altair chart object
    """
    if df.empty:
        return None
    
    # Prepare data - need to melt the dataframe
    metrics = ['Coherence Score', 'Quality Score', 'Capture Rate', 'Hallucination Score']
    id_vars = ['Section Title']
    
    # Melt dataframe to have metric-value pairs
    melted_df = pd.melt(
        df[id_vars + metrics], 
        id_vars=id_vars, 
        value_vars=metrics,
        var_name='Metric',
        value_name='Score'
    )
    
    # Clean up metric names
    melted_df['Metric'] = melted_df['Metric'].str.replace(' Score', '')
    
    # Create heatmap
    heatmap = alt.Chart(melted_df).mark_rect().encode(
        x=alt.X('Section Title:N', title='Section', sort=None),
        y=alt.Y('Metric:N', title=None),
        color=alt.Color(
            'Score:Q', 
            scale=alt.Scale(domain=[0, 0.5, 1], range=['#dc3545', '#ffc107', '#28a745']),
        ),
        tooltip=['Section Title', 'Metric', 'Score']
    ).properties(
        title="Evaluation Metrics Across Sections",
        width=600,
        height=300
    )
    
    # Add text labels
    text = alt.Chart(melted_df).mark_text(baseline='middle').encode(
        x=alt.X('Section Title:N'),
        y=alt.Y('Metric:N'),
        text=alt.Text('Score:Q', format='.2f'),
        color=alt.condition(
            alt.datum.Score > 0.5,
            alt.value('black'),
            alt.value('white')
        )
    )
    
    return heatmap + text

def display_dashboard(results_dir):
    """
    Display the main dashboard with visualizations.
    
    Args:
        results_dir: Directory containing evaluation results
    """
    st.header("Evaluation Dashboard")
    
    # Load all evaluation results
    all_results = load_all_evaluation_results(results_dir)
    
    if all_results.empty:
        st.warning(f"No evaluation results found in {results_dir}")
        st.info("Run the evaluation tool first to generate results.")
        return
    
    # Overview section with summary statistics
    st.subheader("Overview")
    
    avg_scores = {
        'Coherence': all_results['Coherence Score'].mean(),
        'Quality': all_results['Quality Score'].mean(),
        'Capture Rate': all_results['Capture Rate'].mean(),
        'Hallucination': 1 - all_results['Hallucination Score'].mean()  # Invert hallucination
    }
    
    # Create metrics in a row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Average Coherence", f"{avg_scores['Coherence']:.2f}")
    with col2:
        st.metric("Average Quality", f"{avg_scores['Quality']:.2f}")
    with col3:
        st.metric("Average Capture", f"{avg_scores['Capture Rate']:.2f}")
    with col4:
        st.metric("Average Accuracy", f"{avg_scores['Hallucination']:.2f}")
    
    # Overall average score
    overall_avg = np.mean(list(avg_scores.values()))
    
    # Create a color code based on score
    if overall_avg > 0.8:
        color = "green"
    elif overall_avg > 0.6:
        color = "lightgreen"
    elif overall_avg > 0.4:
        color = "orange"
    else:
        color = "red"
    
    st.markdown(f"""
    <div style="border:1px solid {color}; border-radius:10px; padding:15px; margin:10px 0; text-align:center; background-color:rgba(0,0,0,0.05);">
        <h2>Overall Documentation Score: <span style="color:{color};">{overall_avg:.2f}</span></h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Visualizations
    st.subheader("Visualizations")
    
    # Create tabs for different visualizations
    viz_tabs = st.tabs(["Metrics Comparison", "Individual Metrics", "Section Comparison"])
    
    with viz_tabs[0]:
        overall_chart = create_overall_chart(all_results)
        if overall_chart:
            st.altair_chart(overall_chart, use_container_width=True)
        else:
            st.info("No data available for chart.")
    
    with viz_tabs[1]:
        # Individual metric charts
        coherence_chart = create_metric_chart(all_results, 'Coherence Score')
        quality_chart = create_metric_chart(all_results, 'Quality Score')
        capture_chart = create_metric_chart(all_results, 'Capture Rate')
        # For hallucination, lower is better
        hallucination_chart = create_metric_chart(all_results, 'Hallucination Score', inverted=True)
        
        metric_select = st.selectbox(
            "Select Metric to View",
            ["Coherence", "Quality", "Capture Rate", "Hallucination"]
        )
        
        if metric_select == "Coherence" and coherence_chart:
            st.altair_chart(coherence_chart, use_container_width=True)
        elif metric_select == "Quality" and quality_chart:
            st.altair_chart(quality_chart, use_container_width=True)
        elif metric_select == "Capture Rate" and capture_chart:
            st.altair_chart(capture_chart, use_container_width=True)
        elif metric_select == "Hallucination" and hallucination_chart:
            st.altair_chart(hallucination_chart, use_container_width=True)
        else:
            st.info("No data available for selected chart.")
    
    with viz_tabs[2]:
        heatmap = create_section_comparison(all_results)
        if heatmap:
            st.altair_chart(heatmap, use_container_width=True)
        else:
            st.info("No data available for heatmap.")
    
    # Areas for improvement
    st.subheader("Areas for Improvement")
    
    # Find lowest scoring sections for each metric
    lowest_coherence = all_results.loc[all_results['Coherence Score'].idxmin()]
    lowest_quality = all_results.loc[all_results['Quality Score'].idxmin()]
    lowest_capture = all_results.loc[all_results['Capture Rate'].idxmin()]
    highest_hallucination = all_results.loc[all_results['Hallucination Score'].idxmax()]
    
    improvement_col1, improvement_col2 = st.columns(2)
    
    with improvement_col1:
        st.markdown("#### Coherence")
        st.markdown(f"**Lowest Score:** {lowest_coherence['Coherence Score']:.2f}")
        st.markdown(f"**Section:** {lowest_coherence['Section Title']}")
        st.markdown(f"**Comment:** {lowest_coherence['Coherence Comment']}")
        
        st.markdown("#### Quality")
        st.markdown(f"**Lowest Score:** {lowest_quality['Quality Score']:.2f}")
        st.markdown(f"**Section:** {lowest_quality['Section Title']}")
        st.markdown(f"**Comment:** {lowest_quality['Quality Comment']}")
    
    with improvement_col2:
        st.markdown("#### Capture Rate")
        st.markdown(f"**Lowest Score:** {lowest_capture['Capture Rate']:.2f}")
        st.markdown(f"**Section:** {lowest_capture['Section Title']}")
        st.markdown(f"**Comment:** {lowest_capture['Capture Comment']}")
        
        st.markdown("#### Hallucination")
        st.markdown(f"**Highest Score:** {highest_hallucination['Hallucination Score']:.2f}")
        st.markdown(f"**Section:** {highest_hallucination['Section Title']}")
        st.markdown(f"**Comment:** {highest_hallucination['Hallucination Comment']}")