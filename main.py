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
            'probability_base_case': 0.5  # Added a probability for the base case
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

    def calculate_normal_distribution_params(self, base, low, high, probability_base_case):
        # Calculate mean and standard deviation for normal distribution with base case probability
        mean = (base * probability_base_case) + (low * (1 - probability_base_case) / 2) + (high * (1 - probability_base_case) / 2)
        # Adjust the standard deviation to account for the probability of the base case
        std_dev = (high - low) / (2 * 1.645) * (1 - probability_base_case)  # Using 1.645 since it is the z-score for the 90th percentile
        return mean, std_dev

    def calculate_score(self):
        total = 0
        for v in self.factors.values():
            mean, std_dev = self.calculate_normal_distribution_params(
                v['base_case'], v['worst_case'], v['best_case'], v['probability_base_case']
            )
            # Draw a sample from the normal distribution
            sample = np.random.normal(mean, std_dev)
            total += v['rank'] * sample
        return total

    def monte_carlo_simulation(self, num_simulations=1000):
        outcomes = []
        for _ in range(num_simulations):
            outcomes.append(self.calculate_score())
        return outcomes


def display_simulation_results(outcomes, decision_title, user_input_title):
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
    ax.set_title(f'Distribution for {decision_title}: {user_input_title}')  # This line ensures the option name is in the title
    ax.legend()
    st.pyplot(fig)

    # This block of code adds the option titles to the sidebar.
    combined_title = f"{decision_title}: {user_input_title}"
    st.sidebar.write(f"**{combined_title}**")
    st.sidebar.write(f"Mean: {mean_outcome:.2f}")
    st.sidebar.write(f"25th Percentile: {percentile_25:.2f}")
    st.sidebar.write(f"75th Percentile: {percentile_75:.2f}")
    st.sidebar.write("-----")


def show_app():
    st.subheader("Enter up to 3 options you're weighing:")
    option_titles = ["Option A", "Option B", "Option C"]
    options = {}

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
            best_case_key = f"{title}_{factor}_best_case"
            worst_case_key = f"{title}_{factor}_worst_case"

            col1, col2, col3 = st.columns(3)
            with col1:
                base_case_value = st.slider(
                    "Base Case (0-3)", min_value=0.0, max_value=3.0,
                    value=1.5, step=0.01, key=base_case_key
                )
                base_case_probability = st.slider(  # Add this slider for base case probability
                    "Probability of Base Case", min_value=0.0, max_value=1.0,
                    value=0.5, step=0.01, key=f"{base_case_key}_prob"
                )
            with col2:
                best_case_value = st.slider(
                    "High Case (Top 90%) (0-3)", min_value=0.0, max_value=3.0,
                    value=2.5, step=0.01, key=best_case_key
                )
            with col3:
                worst_case_value = st.slider(
                    "Low Case (Bottom 10%) (0-3)", min_value=0.0, max_value=3.0,
                    value=0.5, step=0.01, key=worst_case_key
                )

            # Update the factors for the current choice object
            choice.factors[factor]['base_case'] = base_case_value
            choice.factors[factor]['probability_base_case'] = base_case_probability
            choice.factors[factor]['best_case'] = best_case_value
            choice.factors[factor]['worst_case'] = worst_case_value

            st.markdown("---")

    # Monte Carlo Simulation Parameters and Execution
    num_simulations = st.slider("Number of simulations:", min_value=10000, max_value=100000, value=30000, step=10000)
    results_summary = {}

    if st.button("Run Simulation"):
        for placeholder_title, choice in choices.items():
            outcomes = choice.monte_carlo_simulation(num_simulations)
            user_input_title = options[placeholder_title]
            display_simulation_results(outcomes, placeholder_title, user_input_title)
            combined_title = f"{placeholder_title}: {user_input_title}"
            results_summary[combined_title] = {
                "mean": np.mean(outcomes),
                "25th_percentile": np.percentile(outcomes, 25),
                "75th_percentile": np.percentile(outcomes, 75),
            }

    if results_summary:
        st.sidebar.header("Ranking Summary")
        mean_ranking = sorted(results_summary, key=lambda x: results_summary[x]["mean"], reverse=True)
        st.sidebar.subheader("Rank by Mean")
        for user_input_title in mean_ranking:
            st.sidebar.write(f"{user_input_title}: {results_summary[user_input_title]['mean']:.2f}")

        spread_ranking = sorted(
            results_summary,
            key=lambda x: results_summary[x]["75th_percentile"] - results_summary[x]["25th_percentile"]
        )
        st.sidebar.subheader("Rank by Spread")
        for user_input_title in spread_ranking:
            spread = results_summary[user_input_title]["75th_percentile"] - results_summary[user_input_title]["25th_percentile"]
            st.sidebar.write(f"{user_input_title}: {spread:.2f}")

# Ensure that the CareerChoice class and other functions are defined above this point
if __name__ == "__main__":
    st.title("Thinking Analytically About Your Career")
    show_app()



