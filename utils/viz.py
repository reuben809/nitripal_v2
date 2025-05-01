import streamlit as st
import altair as alt
import pandas as pd
from datetime import datetime, timedelta

def create_nutrition_chart(nutrition_data):
    """
    Create line charts for nutrition data
    
    Args:
        nutrition_data: List of nutrition data points by date
        
    Returns:
        Altair chart
    """
    if not nutrition_data:
        return None
    
    # Convert to DataFrame
    df = pd.DataFrame(nutrition_data)
    
    # Ensure we have a date column
    if 'date' not in df.columns:
        return None
    
    # Melt the DataFrame for Altair
    df_melted = df.melt(
        id_vars=['date'],
        value_vars=['calories', 'protein', 'carbs', 'fat'],
        var_name='nutrient',
        value_name='value'
    )
    
    # Create chart
    chart = alt.Chart(df_melted).mark_line(point=True).encode(
        x=alt.X('date:T', title='Date'),
        y=alt.Y('value:Q', title='Amount'),
        color=alt.Color('nutrient:N', legend=alt.Legend(title="Nutrient")),
        tooltip=['date:T', 'nutrient:N', 'value:Q']
    ).properties(
        title='Nutrition Intake Over Time',
        width=600,
        height=300
    ).interactive()
    
    return chart

def create_macronutrient_pie_chart(nutrition_data, date=None):
    """
    Create pie chart for macronutrient breakdown
    
    Args:
        nutrition_data: List of nutrition data points
        date: Optional specific date to show
        
    Returns:
        Altair chart
    """
    if not nutrition_data:
        return None
    
    # Convert to DataFrame
    df = pd.DataFrame(nutrition_data)
    
    # Filter by date if specified
    if date:
        df = df[df['date'] == date]
    
    # If no data remains after filtering, use the most recent date
    if df.empty and nutrition_data:
        latest_date = max(item['date'] for item in nutrition_data)
        df = pd.DataFrame([item for item in nutrition_data if item['date'] == latest_date])
    
    # If still empty, return None
    if df.empty:
        return None
    
    # Calculate sum for each nutrient
    nutrient_sum = {
        'Protein': df['protein'].sum(),
        'Carbs': df['carbs'].sum(),
        'Fat': df['fat'].sum()
    }
    
    # Create data for pie chart
    pie_data = pd.DataFrame({
        'nutrient': list(nutrient_sum.keys()),
        'value': list(nutrient_sum.values())
    })
    
    # Create chart
    chart = alt.Chart(pie_data).mark_arc().encode(
        theta=alt.Theta(field="value", type="quantitative"),
        color=alt.Color(field="nutrient", type="nominal", legend=alt.Legend(title="Macronutrient")),
        tooltip=['nutrient', 'value']
    ).properties(
        title='Macronutrient Distribution',
        width=300,
        height=300
    )
    
    return chart

def create_meal_frequency_chart(meal_pattern_data):
    """
    Create bar chart for meal frequency
    
    Args:
        meal_pattern_data: Dictionary with meal frequency information
        
    Returns:
        Altair chart
    """
    meal_count = meal_pattern_data.get('meal_types_count', {})
    
    if not meal_count:
        return None
    
    # Create data for chart
    df = pd.DataFrame({
        'meal': list(meal_count.keys()),
        'count': list(meal_count.values())
    })
    
    # Create chart
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('meal:N', title='Meal Type'),
        y=alt.Y('count:Q', title='Frequency'),
        color=alt.Color('meal:N', legend=None),
        tooltip=['meal', 'count']
    ).properties(
        title='Meal Frequency',
        width=300,
        height=200
    )
    
    return chart

def create_xp_progress_chart(user_stats):
    """
    Create a progress bar for XP
    
    Args:
        user_stats: Dictionary with user XP information
        
    Returns:
        HTML for progress bar
    """
    xp = user_stats.get('xp', 0)
    next_level_xp = user_stats.get('next_level_xp', 100)
    current_level_xp = user_stats.get('current_level_xp', 0)
    
    # Calculate percentage
    if next_level_xp > current_level_xp:
        percentage = ((xp - current_level_xp) / (next_level_xp - current_level_xp)) * 100
    else:
        percentage = 100
    
    # HTML for a custom styled progress bar
    html = f"""
    <div style="margin-top:10px; margin-bottom:20px;">
        <p style="margin-bottom:5px;">Level Progress: {xp - current_level_xp}/{next_level_xp - current_level_xp} XP</p>
        <div style="width:100%; background-color:#f0f0f0; border-radius:5px; height:20px;">
            <div style="width:{percentage}%; background-color:#4CAF50; height:20px; border-radius:5px;"></div>
        </div>
    </div>
    """
    
    return html

def create_weekly_calendar(meals_by_date, start_date=None):
    """
    Create a visual weekly calendar with meals
    
    Args:
        meals_by_date: Dictionary mapping dates to meals
        start_date: Starting date for the calendar
        
    Returns:
        Nothing, creates UI elements directly
    """
    # If no start date provided, use the beginning of the current week
    if not start_date:
        today = datetime.now()
        start_date = today - timedelta(days=today.weekday())
    
    # Create date range for the week
    dates = [start_date + timedelta(days=i) for i in range(7)]
    date_strings = [d.strftime('%Y-%m-%d') for d in dates]
    day_names = [d.strftime('%A') for d in dates]
    
    # Create columns for each day
    cols = st.columns(7)
    
    # Display day names
    for col, day in zip(cols, day_names):
        col.markdown(f"**{day}**")
    
    # Display dates
    for col, date in zip(cols, date_strings):
        col.markdown(f"{date}")
    
    # Display meals for each date
    for meal_type in ["Breakfast", "Lunch", "Dinner", "Snack"]:
        st.markdown(f"### {meal_type}")
        meal_cols = st.columns(7)
        
        for col, date in zip(meal_cols, date_strings):
            meals_for_date = meals_by_date.get(date, [])
            meals_of_type = [meal for meal in meals_for_date if meal.get('meal_type', '').lower() == meal_type.lower()]
            
            if meals_of_type:
                for meal in meals_of_type:
                    with col.expander(f"{meal_type}", expanded=False):
                        st.write(meal.get('description', 'No description'))
            else:
                col.text("No meal")
