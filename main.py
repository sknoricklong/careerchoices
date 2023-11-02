import streamlit as st
import random
import numpy as np
import matplotlib.pyplot as plt


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
    decision_title = st.text_input("Enter the option you're weighing:", "")
    decision_title = decision_title

    if not decision_title:
        st.warning("Please enter a decision title to proceed.")
        return

    choice = CareerChoice()
    all_factors = list(choice.factors.keys())
    selected_factors = []

    st.subheader("Rank the factors by importance:")

    for i in range(len(all_factors)):
        remaining_factors = [factor for factor in all_factors if factor not in selected_factors]
        selected_factor = st.selectbox(f"**Rank {i + 1}:**", remaining_factors, index=0)
        selected_factors.append(selected_factor)

        st.markdown(f"### {selected_factor}")

        # Base Case
        col1, col2 = st.columns(2)
        with col1:
            choice.factors[selected_factor]['base_case'] = st.slider(
                f"Base Case meets need (0-3)", 0.0, 3.0,
                float(choice.factors[selected_factor]['base_case']), 0.25,
                key=f"{selected_factor}_base_case_slider"  # unique key
            )
        with col2:
            prob_base = st.slider(
                f"Probability of Base Case (0-1)", 0.0, 1.0,
                float(choice.factors[selected_factor]['prob_base']), 0.01,
                key=f"{selected_factor}_base_prob_slider"  # unique key
            )
            choice.factors[selected_factor]['prob_base'] = prob_base

        # Best Case
        col1, col2 = st.columns(2)
        with col1:
            choice.factors[selected_factor]['best_case'] = st.slider(
                f"Best Case meets need (0-3)", 0.0, 3.0,
                float(choice.factors[selected_factor]['best_case']), 0.25,
                key=f"{selected_factor}_best_case_slider"  # unique key
            )
        with col2:
            prob_best = st.slider(
                f"Probability of Best Case (0-{1 - prob_base:.2f})", 0.0, 1.0 - prob_base,
                float(choice.factors[selected_factor]['prob_best']), 0.01,
                key=f"{selected_factor}_best_prob_slider"  # unique key
            )
            choice.factors[selected_factor]['prob_best'] = prob_best

        # Worst Case
        col1, col2 = st.columns(2)
        with col1:
            choice.factors[selected_factor]['worst_case'] = st.slider(
                f"Worst Case meets need (0-3)", 0.0, 3.0,
                float(choice.factors[selected_factor]['worst_case']), 0.25,
                key=f"{selected_factor}_worst_case_slider"  # unique key
            )
        with col2:
            prob_worst = 1.0 - prob_best - prob_base
            st.write(f"Probability of Worst Case: {prob_worst:.2f}")
            choice.factors[selected_factor]['prob_worst'] = prob_worst

        st.markdown("---")

    st.subheader("Monte Carlo Simulation Parameters")
    num_simulations = st.slider("Number of simulations:", 100, 5000, 5000)

    if st.button("Run Simulation"):
        outcomes = choice.monte_carlo_simulation(num_simulations)
        display_simulation_results(outcomes, decision_title)



if __name__ == "__main__":
    st.title("Career Choice Decision Helper")
    show_app()
