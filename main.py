import streamlit as st
import random
import numpy as np
import matplotlib.pyplot as plt


class CareerChoice:
    def __init__(self):
        self.initialize_factors()

    def initialize_factors(self):
        default_factor = {
            'rank': 0,
            'base_case': 0.00,
            'best_case': 0.00,
            'worst_case': 0.00,
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

    def calculate_normal_distribution_params(self, base, low, high):
        # Calculate mean and standard deviation for normal distribution
        mean = (base + low + high) / 3
        std_dev = (high - low) / 6  # Assuming a 99.7% range for standard deviation
        return mean, std_dev

    def calculate_score(self):
        total = 0
        for v in self.factors.values():
            mean, std_dev = self.calculate_normal_distribution_params(
                v['base_case'], v['worst_case'], v['best_case']
            )
            # Draw a sample from the normal distribution
            sample = np.random.normal(mean, std_dev)
            total += v['rank'] * sample
        return total

    def monte_carlo_simulation(self, num_simulations=10000):
        outcomes = []
        for _ in range(num_simulations):
            outcomes.append(self.calculate_score())
        return outcomes


def display_simulation_results(outcomes, decision_title, user_input_title, min_score, max_score):
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
    ax.set_xlim(min_score, max_score)
    ax.set_title(f'Distribution for {decision_title}: {user_input_title}')
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

    # Predefined values for "Privacy in Seattle"
    predefined_privacy = {
        'Community': (1.4, 2.0, 0.25),
        'Career Setup': (2.45, 2.55, 1.3),
        'Public Impact': (1.5, 2.1, 1.0),
        'Job Satisfaction': (1.75, 2.7, 1.25),
        'Pay': (2.0, 2.55, 1.5),
        'Nature/Weather': (1.5, 2.5, 1.1)
    }

    predefined_antitrust = {
        'Community': (2.25, 2.8, 1.7),
        'Career Setup': (2.4, 2.5, 1.85),
        'Public Impact': (0.25, 0.75, 0.0),
        'Job Satisfaction': (1.0, 1.5, 0.2),
        'Pay': (2.9, 3.0, 2.6),
        'Nature/Weather': (2.0, 2.2, 1.5)
    }

    predefined_tech = {
        'Community': (2.25, 2.6, 1.5),
        'Career Setup': (1.85, 3.0, 1.15),
        'Public Impact': (2.0, 2.85, 1.3),
        'Job Satisfaction': (1.9, 3.0, 0.4),
        'Pay': (0.75, 1.35, 0.15),
        'Nature/Weather': (2.0, 2.5, 1.4)
    }

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

            # Check if the option is "Privacy in Seattle" and set predefined values if it is
            if options[title] == "Privacy in Seattle" and factor in predefined_privacy:
                base, high, low = predefined_privacy[factor]
            elif options[title] == "Antitrust in DC" and factor in predefined_antitrust:
                base, high, low = predefined_antitrust[factor]
            elif options[title] == "Tech in DC" and factor in predefined_tech:
                base, high, low = predefined_tech[factor]
            else:
                base = 1.5
                high = 2.5
                low = 0.5

            base_case_key = f"{title}_{factor}_base_case"
            best_case_key = f"{title}_{factor}_best_case"
            worst_case_key = f"{title}_{factor}_worst_case"

            col1, col2, col3 = st.columns(3)
            with col1:
                base_case_value = st.slider(
                    "Base Case (0-3)", min_value=0.0, max_value=3.0,
                    value=base, step=0.05, key=base_case_key
                )
            with col2:
                best_case_value = st.slider(
                    "High Case (Top 90%) (0-3)", min_value=0.0, max_value=3.0,
                    value=high, step=0.05, key=best_case_key
                )
            with col3:
                worst_case_value = st.slider(
                    "Low Case (Bottom 10%) (0-3)", min_value=0.0, max_value=3.0,
                    value=low, step=0.05, key=worst_case_key
                )

            # Update the factors for the current choice object
            choice.factors[factor]['base_case'] = base_case_value
            choice.factors[factor]['best_case'] = best_case_value
            choice.factors[factor]['worst_case'] = worst_case_value

            st.markdown("---")

    global_min_score = float('inf')
    global_max_score = float('-inf')

    # Monte Carlo Simulation Parameters and Execution
    num_simulations = st.slider("Number of simulations:", min_value=10000, max_value=100000, value=10000, step=10000)
    results_summary = {}
    all_outcomes = []

    def display_box_and_whisker_plot(results_summary, global_min_score, global_max_score):
        fig, ax = plt.subplots()

        # Sort the data by best case (e.g., mean)
        sorted_titles = sorted(results_summary, key=lambda x: results_summary[x]['mean'], reverse=True)

        # Prepare sorted data for the box plot
        data = [results_summary[title]['outcomes'] for title in sorted_titles]

        # Create the box plot
        box = ax.boxplot(data, labels=sorted_titles, showfliers=False, patch_artist=True)

        ax.set_xlabel('Options')
        ax.set_ylabel('Score')
        ax.set_ylim(global_min_score, global_max_score)
        ax.set_title('Box and Whisker Plot of Career Options')

        # Rotate labels for better readability
        plt.xticks(rotation=45)

        st.pyplot(fig)

    # Modify the button click logic
    if st.button("Run Simulation"):
        # Initialize a dictionary to store the outcomes for each option
        results_summary = {}

        # Run the Monte Carlo simulation for each option and collect outcomes
        for title, choice in choices.items():
            outcomes = choice.monte_carlo_simulation(num_simulations)
            mean_outcome = np.mean(outcomes)
            percentile_25 = np.percentile(outcomes, 25)
            percentile_75 = np.percentile(outcomes, 75)

            results_summary[options[title]] = {
                'outcomes': outcomes,
                'mean': mean_outcome,
                '25th_percentile': percentile_25,
                '75th_percentile': percentile_75,
            }

        # Determine global min and max scores from all collected outcomes
        all_outcomes = [outcome for res in results_summary.values() for outcome in res['outcomes']]
        global_min_score = min(all_outcomes) if all_outcomes else None
        global_max_score = max(all_outcomes) if all_outcomes else None

        # Display the box and whisker plot
        display_box_and_whisker_plot(results_summary, global_min_score, global_max_score)

    if results_summary:
        st.sidebar.header("Ranking Summary")
        # Update the ranking display logic
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
            spread = results_summary[user_input_title]["75th_percentile"] - results_summary[user_input_title][
                "25th_percentile"]
            st.sidebar.write(f"{user_input_title}: {spread:.2f}")

# Ensure that the CareerChoice class and other functions are defined above this point
if __name__ == "__main__":
    st.title("Thinking Analytically About Your Career")
    show_app()
