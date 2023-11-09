import streamlit as st
import random
import numpy as np
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import base64
import io

def generate_pdf(outcomes, results_summary):
    pdf_output = io.BytesIO()
    c = canvas.Canvas(pdf_output, pagesize=letter)
    width, height = letter

    y_position = height - 30

    for title, stats in results_summary.items():
        c.drawString(30, y_position, f"Stats for {title}")
        y_position -= 20
        c.drawString(30, y_position, f"Mean: {stats['mean']:.2f}")
        y_position -= 20
        c.drawString(30, y_position, f"25th Percentile: {stats['25th_percentile']:.2f}")
        y_position -= 20
        c.drawString(30, y_position, f"75th Percentile: {stats['75th_percentile']:.2f}")
        y_position -= 20

        fig = plt.figure()
        display_simulation_results(outcomes[title], title)
        image_stream = save_fig_to_png(fig)
        plt.close(fig)

        image = ImageReader(image_stream)
        c.drawImage(image, 30, y_position, width=500, preserveAspectRatio=True, anchor='c')
        y_position -= 240  # Adjust as necessary based on your image sizes

        if y_position < 100:  # Check to avoid drawing over the bottom page limit
            c.showPage()
            y_position = height - 30

    c.save()
    pdf_output.seek(0)

    return pdf_output

class CareerChoice:
    def __init__(self):
        self.initialize_factors()

    def initialize_factors(self):
        self.factors = {
            'Community': {
                'rank': 1,
                'base_case': 3.00,
                'best_case': 0.00,
                'worst_case': 0.00,
                'prob_best': 0.0,
                'prob_worst': 0.0,
                'prob_base': 0.5  # Added this line
            },
            'Career Setup': {
                'rank': 2,
                'base_case': 2.50,
                'best_case': 0.00,
                'worst_case': 0.00,
                'prob_best': 0.0,
                'prob_worst': 0.0,
                'prob_base': 0.5  # Added this line
            },
            'Public Impact': {
                'rank': 3,
                'base_case': 0.00,
                'best_case': 0.00,
                'worst_case': 0.00,
                'prob_best': 0.0,
                'prob_worst': 0.0,
                'prob_base': 0.5  # Added this line
            },
            'Job Satisfaction': {
                'rank': 4,
                'base_case': 1.00,
                'best_case': 0.00,
                'worst_case': 0.00,
                'prob_best': 0.0,
                'prob_worst': 0.0,
                'prob_base': 0.5  # Added this line
            },
            'Pay': {
                'rank': 5,
                'base_case': 3.00,
                'best_case': 0.00,
                'worst_case': 0.00,
                'prob_best': 0.0,
                'prob_worst': 0.0,
                'prob_base': 0.5  # Added this line
            },
            'Weather': {
                'rank': 6,
                'base_case': 2.00,
                'best_case': 0.00,
                'worst_case': 0.00,
                'prob_best': 0.0,
                'prob_worst': 0.0,
                'prob_base': 0.5  # Added this line
            },
        }

    def calculate_score(self):
        total = 0
        for v in self.factors.values():
            rand_val = random.random()
            if rand_val < v['prob_best']:
                total += v['rank'] * v['best_case']
            elif rand_val < (v['prob_best'] + v['prob_base']):
                total += v['rank'] * v['base_case']
            else:
                total += v['rank'] * v['worst_case']
        return total

    def monte_carlo_simulation(self, num_simulations=1000):
        outcomes = []
        for _ in range(num_simulations):
            outcomes.append(self.calculate_score())
        return outcomes


def display_simulation_results(outcomes, decision_title):
    fig, ax = plt.subplots()
    ax.hist(outcomes, bins=30, edgecolor='k', alpha=0.75)

    mean_outcome = np.mean(outcomes)
    percentile_25 = np.percentile(outcomes, 25)
    percentile_75 = np.percentile(outcomes, 75)

    ax.axvline(mean_outcome, color='red', linestyle='dashed', linewidth=1, label=f'Mean: {mean_outcome:.2f}')
    ax.axvline(percentile_25, color='blue', linestyle='dashed', linewidth=1,
               label=f'25th percentile: {percentile_25:.2f}')
    ax.axvline(percentile_75, color='green', linestyle='dashed', linewidth=1,
               label=f'75th percentile: {percentile_75:.2f}')

    ax.set_xlabel('Score')
    ax.set_ylabel('Frequency')
    ax.set_title(f'Distribution for {decision_title}')
    ax.legend()
    st.pyplot(fig)

    st.sidebar.write(f"**{decision_title}**")
    st.sidebar.write(f"Mean: {mean_outcome:.2f}")
    st.sidebar.write(f"25th Percentile: {percentile_25:.2f}")
    st.sidebar.write(f"75th Percentile: {percentile_75:.2f}")
    st.sidebar.write("-----")


def show_app():
    st.subheader("Enter up to 3 options you're weighing:")
    options = []
    for i in range(3):
        option_title = st.text_input(f"Option {i+1} title:", key=f"option_{i}")
        if option_title:
            options.append(option_title)

    if len(options) == 0:
        st.warning("Please enter at least one option title to proceed.")
        return

    choices = [CareerChoice() for _ in options]

    results_summary = {}

    for index, choice in enumerate(choices):
        decision_title = options[index]

        all_factors = list(choice.factors.keys())
        selected_factors = []

        st.markdown(f"## Option {index + 1}: {decision_title}")
        st.markdown("Rank the factors by importance:")

        for i, _ in enumerate(all_factors):
            remaining_factors = [factor for factor in all_factors if factor not in selected_factors]
            selected_factor = st.selectbox(f"Option {index + 1} - Rank {i + 1}:", remaining_factors, index=0, key=f"option_{index}_rank_{i}")
            selected_factors.append(selected_factor)

            st.markdown(f"### **Rank {i + 1}: {selected_factor}**")

            # Unique keys using both option index and rank index
            base_case_key = f"option_{index}_rank_{i}_base_case"
            base_prob_key = f"option_{index}_rank_{i}_prob_base"
            best_case_key = f"option_{index}_rank_{i}_best_case"
            best_prob_key = f"option_{index}_rank_{i}_prob_best"
            worst_case_key = f"option_{index}_rank_{i}_worst_case"

            # Base Case
            col1, col2 = st.columns(2)
            with col1:
                choice.factors[selected_factor]['base_case'] = st.slider(
                    f"Base Case meets need (0-3)", 0.0, 3.0,
                    value=float(choice.factors[selected_factor]['base_case']), step=0.25,
                    key=base_case_key
                )
            with col2:
                prob_base = st.slider(
                    f"Probability of Base Case (0-1)", 0.0, 1.0,
                    value=float(choice.factors[selected_factor]['prob_base']), step=0.01,
                    key=base_prob_key
                )
                choice.factors[selected_factor]['prob_base'] = prob_base

            # Best Case
            col1, col2 = st.columns(2)
            with col1:
                choice.factors[selected_factor]['best_case'] = st.slider(
                    f"Best Case meets need (0-3)", 0.0, 3.0,
                    value=float(choice.factors[selected_factor]['best_case']), step=0.25,
                    key=best_case_key
                )
            with col2:
                prob_best = st.slider(
                    f"Probability of Best Case (0-{1 - prob_base:.2f})", 0.0, 1.0 - prob_base,
                    value=float(choice.factors[selected_factor]['prob_best']), step=0.01,
                    key=best_prob_key
                )
                choice.factors[selected_factor]['prob_best'] = prob_best

            # Worst Case
            col1, col2 = st.columns(2)
            with col1:
                choice.factors[selected_factor]['worst_case'] = st.slider(
                    f"Worst Case meets need (0-3)", 0.0, 3.0,
                    value=float(choice.factors[selected_factor]['worst_case']), step=0.25,
                    key=worst_case_key
                )
            with col2:
                prob_worst = 1.0 - prob_best - prob_base
                st.write(f"Probability of Worst Case: {prob_worst:.2f}")
                choice.factors[selected_factor]['prob_worst'] = prob_worst

            st.markdown("---")

    st.subheader("Monte Carlo Simulation Parameters")
    num_simulations = st.slider(
        "Number of simulations:",
        10000, 100000, 30000, 10000,
        key="num_simulations"
    )

    if st.button("Run Simulation"):
        outcomes_dict = {}  # Initialize a dictionary to hold outcomes for all options
        for index, choice in enumerate(choices):
            decision_title = options[index]
            outcomes = choice.monte_carlo_simulation(num_simulations)
            display_simulation_results(outcomes, decision_title)
            outcomes_dict[decision_title] = outcomes  # Store outcomes in the dictionary

            # Collect summary statistics for sidebar display later
            results_summary[decision_title] = {
                "mean": np.mean(outcomes),
                "25th_percentile": np.percentile(outcomes, 25),
                "75th_percentile": np.percentile(outcomes, 75),
            }

    # Sidebar ranking display
    if results_summary:
        st.sidebar.header("Ranking Summary")

        # Sort by mean and get the titles
        mean_ranking = sorted(results_summary, key=lambda x: results_summary[x]["mean"], reverse=True)
        st.sidebar.subheader("Rank by Mean")
        for title in mean_ranking:
            st.sidebar.write(f"{title}: {results_summary[title]['mean']:.2f}")

        # Sort by spread (75th percentile - 25th percentile) and get the titles
        spread_ranking = sorted(
            results_summary,
            key=lambda x: results_summary[x]["75th_percentile"] - results_summary[x]["25th_percentile"]
        )
        st.sidebar.subheader("Rank by Spread")
        for title in spread_ranking:
            spread = results_summary[title]["75th_percentile"] - results_summary[title]["25th_percentile"]
            st.sidebar.write(f"{title}: {spread:.2f}")


if __name__ == "__main__":
    st.title("Think Analytically About Your Career")
    show_app()



