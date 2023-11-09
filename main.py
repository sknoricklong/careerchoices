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

    def update_ranks(self, selected_factors):
        # This function should be called after the user has finished ranking the factors for an option.
        # It updates the rank for each factor based on the order in which they were selected.
        for i, factor in enumerate(selected_factors):
            self.factors[factor]['rank'] = i + 1


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
    options = [st.text_input(f"Option {i+1} title:", key=f"option_{i}") for i in range(3)]
    options = [option for option in options if option]  # Filter out empty options

    if not options:
        st.warning("Please enter at least one option title to proceed.")
        return

    # Initialize or update session state for ranks
    if 'ranks' not in st.session_state:
        st.session_state.ranks = {option: {} for option in options}

    choices = [CareerChoice() for _ in options]

    for index, choice in enumerate(choices):
        decision_title = options[index]

        st.markdown(f"## Option {index + 1}: {decision_title}")
        st.markdown("Rank the factors by importance:")

        for rank in range(len(choice.factors)):
            factor_name = st.session_state.ranks[decision_title].get(rank + 1)

            if factor_name is None:
                # Extract previously ranked factors to prevent re-ranking
                ranked_factors = list(st.session_state.ranks[decision_title].values())
                remaining_factors = [factor for factor in choice.factors if factor not in ranked_factors]

                # Select a factor and assign it a rank
                factor_name = st.selectbox(
                    f"Rank {rank + 1}",
                    remaining_factors,
                    key=f"factor_{index}_{rank}"
                )
                st.session_state.ranks[decision_title][rank + 1] = factor_name

            st.markdown(f"### **Rank {rank + 1}: {factor_name}**")

            # Update the factors in the choice instance with the new rank
            choice.factors[factor_name]['rank'] = rank + 1

            # Display sliders for base, best, and worst cases
            with st.container():
                col1, col2, col3 = st.columns(3)

                with col1:
                    base_case = st.slider(
                        f"Base Case for {factor_name}",
                        0.0, 3.0,
                        value=choice.factors[factor_name]['base_case'],
                        key=f"base_{index}_{rank}"
                    )
                with col2:
                    best_case = st.slider(
                        f"Best Case for {factor_name}",
                        0.0, 3.0,
                        value=choice.factors[factor_name]['best_case'],
                        key=f"best_{index}_{rank}"
                    )
                with col3:
                    worst_case = st.slider(
                        f"Worst Case for {factor_name}",
                        0.0, 3.0,
                        value=choice.factors[factor_name]['worst_case'],
                        key=f"worst_{index}_{rank}"
                    )

                # Update the factors with the new values
                choice.factors[factor_name]['base_case'] = base_case
                choice.factors[factor_name]['best_case'] = best_case
                choice.factors[factor_name]['worst_case'] = worst_case

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



