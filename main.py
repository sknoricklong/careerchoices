import streamlit as st
import random
import numpy as np
import matplotlib.pyplot as plt
import base64
import io


class CareerChoice:
    def __init__(self):
        self.initialize_factors()

    def initialize_factors(self):
        default_factor = {
            'rank': 0,
            'base_case': 0.00,
            'best_case': 0.00,
            'worst_case': 0.00,
            'prob_best': 0.0,
            'prob_worst': 0.0,
            'prob_base': 0.0
        }

        factor_names = [
            'Career Setup',
            'Community',
            'Health',
            'Hobbies',
            'Home Situation',
            'Job Satisfaction',
            'Learning',
            'Location/Where I Live',
            'Mentorship',
            'Pay',
            'Pet',
            'Public Impact',
            'Nature/Weather',
            'Travel'
        ]

        self.factors = {factor: dict(default_factor, rank=i + 1) for i, factor in enumerate(sorted(factor_names))}

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
    option_titles = ["Option A", "Option B", "Option C"]
    options = {}
    results_summary = {}

    for i, title in enumerate(option_titles):
        option_input = st.text_input(f"{title} title:", key=f"option_{i}")
        if option_input:
            options[title] = option_input

    if not options:
        st.warning("Please enter at least one option title to proceed.")
        return

    all_factors = list(CareerChoice().factors.keys())
    selected_factors = st.multiselect("Select your top 6 factors:", all_factors, default=[])

    if len(selected_factors) != 6:
        st.error("Please select exactly 6 factors.")
        return

    choices = {title: CareerChoice() for title in options}

    for index, factor in enumerate(selected_factors, start=1):
        st.markdown(f"## Rank {index}: {factor}")
        for title, choice in choices.items():
            st.markdown(f"### {title}: {options[title]}")

            base_case_key = f"{title}_{factor}_base_case"
            base_prob_key = f"{title}_{factor}_prob_base"
            best_case_key = f"{title}_{factor}_best_case"
            best_prob_key = f"{title}_{factor}_prob_best"
            worst_case_key = f"{title}_{factor}_worst_case"

            # Sliders
            col1, col2 = st.columns(2)
            with col1:
                base_case_value = st.slider(
                    "Base Case meets need (0-3)", min_value=0.0, max_value=3.0,
                    value=0.0, step=0.25, key=base_case_key
                )
            with col2:
                prob_base_value = st.slider(
                    "Probability of Base Case (0-1)", min_value=0.0, max_value=1.0,
                    value=0.0, step=0.01, key=base_prob_key
                )

            col1, col2 = st.columns(2)
            with col1:
                best_case_value = st.slider(
                    "Best Case meets need (0-3)", min_value=0.0, max_value=3.0,
                    value=0.0, step=0.25, key=best_case_key
                )
            with col2:
                prob_best_value = st.slider(
                    "Probability of Best Case (0-1)", min_value=0.0, max_value=1.0 - prob_base_value,
                    value=0.0, step=0.01, key=best_prob_key
                )

            col1, col2 = st.columns(2)
            with col1:
                worst_case_value = st.slider(
                    "Worst Case meets need (0-3)", min_value=0.0, max_value=3.0,
                    value=0.0, step=0.25, key=worst_case_key
                )
            with col2:
                prob_worst_value = 1.0 - prob_best_value - prob_base_value
                st.write(f"Probability of Worst Case: {prob_worst_value:.2f}")

            # Update the factors for the current choice object
            choice.factors[factor]['base_case'] = base_case_value
            choice.factors[factor]['prob_base'] = prob_base_value
            choice.factors[factor]['best_case'] = best_case_value
            choice.factors[factor]['prob_best'] = prob_best_value
            choice.factors[factor]['worst_case'] = worst_case_value
            choice.factors[factor]['prob_worst'] = prob_worst_value

            st.markdown("---")

    # Monte Carlo Simulation Parameters and Execution
    st.subheader("Monte Carlo Simulation Parameters")
    num_simulations = st.slider("Number of simulations:", min_value=10000, max_value=100000, value=30000, step=10000)

    if st.button("Run Simulation"):
        # We need to iterate over the items of choices, not enumerate
        for decision_title, choice in choices.items():
            outcomes = choice.monte_carlo_simulation(num_simulations)
            display_simulation_results(outcomes, decision_title)
            # Update results_summary for each option using the decision_title from the choices dictionary
            results_summary[decision_title] = {
                "mean": np.mean(outcomes),
                "25th_percentile": np.percentile(outcomes, 25),
                "75th_percentile": np.percentile(outcomes, 75),
            }

    # Display results summary in the sidebar
    if results_summary:
        st.sidebar.header("Ranking Summary")
        mean_ranking = sorted(results_summary, key=lambda x: results_summary[x]["mean"], reverse=True)
        st.sidebar.subheader("Rank by Mean")
        for title in mean_ranking:
            st.sidebar.write(f"{title}: {results_summary[title]['mean']:.2f}")

        spread_ranking = sorted(
            results_summary,
            key=lambda x: results_summary[x]["75th_percentile"] - results_summary[x]["25th_percentile"]
        )
        st.sidebar.subheader("Rank by Spread")
        for title in spread_ranking:
            spread = results_summary[title]["75th_percentile"] - results_summary[title]["25th_percentile"]
            st.sidebar.write(f"{title}: {spread:.2f}")

# Ensure that the CareerChoice class and other functions are defined above this point
if __name__ == "__main__":
    st.title("Thinking Analytically About Your Career")
    show_app()



