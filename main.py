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
    options = [st.text_input(f"Option {i+1} title:", key=f"option_{i}") for i in range(3)]
    options = list(filter(None, options))  # Remove empty strings

    if not options:
        st.warning("Please enter at least one option title to proceed.")
        return

    if 'factors' not in st.session_state:
        st.session_state.factors = ['Community', 'Career Setup', 'Public Impact', 'Job Satisfaction', 'Pay', 'Weather']
        st.session_state.factor_rankings = {factor: idx+1 for idx, factor in enumerate(st.session_state.factors)}
        st.session_state.rankings_confirmed = False

    st.markdown("## Rank the factors by importance:")
    all_factors = st.session_state.factors
    for factor in all_factors:
        rank = st.selectbox(
            f"Rank for {factor}:",
            range(1, len(all_factors) + 1),
            index=st.session_state.factor_rankings[factor] - 1,
            key=f"rank_{factor}"
        )
        st.session_state.factor_rankings[factor] = rank

    if st.button("Confirm Rankings"):
        st.session_state.rankings_confirmed = True

    if st.session_state.rankings_confirmed:
        choices = [CareerChoice() for _ in options]
        results_summary = {}

        for index, choice in enumerate(choices):
            decision_title = options[index]
            st.markdown(f"## Option {index + 1}: {decision_title}")

            for factor in all_factors:
                rank = st.session_state.factor_rankings[factor]
                choice.factors[factor]['rank'] = rank  # Set the rank from the confirmed rankings

                base_case_key = f"option_{index}_{factor}_base_case"
                best_case_key = f"option_{index}_{factor}_best_case"
                worst_case_key = f"option_{index}_{factor}_worst_case"

                base_case = st.slider(
                    f"Base Case for {factor} (Rank {rank}):",
                    0.0, 3.0,
                    value=choice.factors[factor]['base_case'],
                    key=base_case_key
                )
                best_case = st.slider(
                    f"Best Case for {factor} (Rank {rank}):",
                    0.0, 3.0,
                    value=choice.factors[factor]['best_case'],
                    key=best_case_key
                )
                worst_case = st.slider(
                    f"Worst Case for {factor} (Rank {rank}):",
                    0.0, 3.0,
                    value=choice.factors[factor]['worst_case'],
                    key=worst_case_key
                )

                choice.factors[factor]['base_case'] = base_case
                choice.factors[factor]['best_case'] = best_case
                choice.factors[factor]['worst_case'] = worst_case

            outcomes = choice.monte_carlo_simulation(num_simulations=1000)
            display_simulation_results(outcomes, decision_title)

            results_summary[decision_title] = {
                "mean": np.mean(outcomes),
                "25th_percentile": np.percentile(outcomes, 25),
                "75th_percentile": np.percentile(outcomes, 75)
            }

        st.sidebar.header("Results Summary")
        for title, stats in results_summary.items():
            st.sidebar.subheader(title)
            st.sidebar.text(f"Mean: {stats['mean']:.2f}")
            st.sidebar.text(f"25th Percentile: {stats['25th_percentile']:.2f}")
            st.sidebar.text(f"75th Percentile: {stats['75th_percentile']:.2f}")


if __name__ == "__main__":
    st.title("Think Analytically About Your Career")
    show_app()



