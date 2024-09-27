import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

MAX_SCORE = 10
MIN_SCORE = 1
NUM_TOT_MATCHES = 23


def read_excel_file(uploaded_file):
    df = pd.read_excel(uploaded_file)
    df.columns = [
        "Nombre",
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9",
        "10",
        "11",
        "12",
        "13",
        "14",
        "15",
        "16",
        "17",
        "18",
        "19",
        "20",
        "21",
        "22",
        "23",
    ]
    df = df.dropna(subset=["Nombre"])
    return df


def process_player_data(df):
    players_data = {}
    for index, row in df.iterrows():
        if row["Nombre"] == "Nombre":
            continue
        player_name = row["Nombre"]
        scores = row[1:].tolist()
        players_data[player_name] = {
            "Scores": scores,
            "Matches_Played": sum([1 for score in scores if score > 0]),
            "Weighted_Score": 0,
            "players_in_match": 0,
            "Normalized_Scores": [0] * NUM_TOT_MATCHES,
        }
    return players_data


def normalize_scores(players_data):
    for match_idx in range(1, NUM_TOT_MATCHES):
        match_scores = [
            players_data[player]["Scores"][match_idx - 1] for player in players_data
        ]
        valid_scores = [score for score in match_scores if score > 0]
        if valid_scores:
            min_score = min(valid_scores)
            max_score = max(valid_scores)
            for player in players_data:
                raw_score = players_data[player]["Scores"][match_idx - 1]
                if raw_score > 0:
                    if max_score - min_score > 0:
                        normalized_score = (
                            (raw_score - min_score) / (max_score - min_score)
                        ) * (MAX_SCORE - MIN_SCORE) + MIN_SCORE
                    else:
                        normalized_score = MIN_SCORE
                    players_data[player]["Normalized_Scores"][
                        match_idx - 1
                    ] = normalized_score
                    players_in_match = sum(
                        1
                        for p in players_data
                        if players_data[p]["Scores"][match_idx - 1] > 0
                    )
                    players_data[player]["Weighted_Score"] += (
                        normalized_score * players_in_match
                    )
                    players_data[player]["players_in_match"] += players_in_match


def calculate_weighted_avg_score(players_data, max_num_matches, magic_factor_flag=0):

    for player, data in players_data.items():
        if data["players_in_match"] > 0:
            if magic_factor_flag == 0:
                data["Weighted_Avg_Score"] = (
                    data["Weighted_Score"]
                    / data["players_in_match"]
                    * data["Matches_Played"]
                    / max_num_matches
                )
            elif magic_factor_flag == 1:
                data["Weighted_Avg_Score"] = (
                    data["Weighted_Score"] / data["players_in_match"]
                )
            elif magic_factor_flag == 2:
                data["Weighted_Avg_Score"] = (
                    data["Weighted_Score"]
                    / data["players_in_match"]
                    * (data["Matches_Played"] / max_num_matches) ** (1 / 2)
                )
        else:
            data["Weighted_Avg_Score"] = 0


def plot_weighted_avg_scores(ax, players_data):
    names = list(players_data.keys())
    avg_scores = [players_data[player]["Weighted_Avg_Score"] for player in names]
    names, avg_scores = zip(
        *sorted(zip(names, avg_scores), key=lambda x: x[1], reverse=True)
    )
    bars = ax.bar(names, avg_scores, color="lightblue")
    return bars, names, avg_scores


def highlight_players(ax, players_data, max_num_matches):
    for player, data in players_data.items():
        if data["Matches_Played"] < 0.6 * max_num_matches:
            ax.bar(
                player,
                players_data[player]["Weighted_Avg_Score"],
                color="gray",
                alpha=0.3,
                hatch="//",
                edgecolor="black",
                linewidth=0,
            )
    winner = max(players_data, key=lambda p: players_data[p]["Weighted_Avg_Score"])
    ax.bar(
        winner,
        players_data[winner]["Weighted_Avg_Score"],
        color="green",
        label="Winner",
    )


def add_labels(ax, bars, avg_scores):
    for bar, score in zip(bars, avg_scores):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            round(score, 2),
            ha="center",
            va="bottom",
        )


# Main script
st.title("Exploding Kittens League Performance Analysis")
st.write("Upload an Excel file with player data to analyze performance.")
uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")

if uploaded_file is not None:
    df = read_excel_file(uploaded_file)
    st.write("Uploaded Data:")
    st.dataframe(df)
    players_data = process_player_data(df)
    max_num_matches = max(
        [players_data[player]["Matches_Played"] for player in players_data]
    )
    normalize_scores(players_data)

    titles = [
        "Weighted Average Scores per Player (With Magic Factor)",
        "Weighted Average Scores per Player (Without Magic Factor)",
        "Weighted Average Scores per Player (With Magic Factor ^ 1/2)",
    ]

    for i in range(3):
        calculate_weighted_avg_score(players_data, max_num_matches, magic_factor_flag=i)
        print(f"Magic Factor: {i}")
        print(players_data["Álvaro"])
        st.subheader(titles[i])
        fig, ax = plt.subplots(figsize=(10, 6))
        bars, names, avg_scores = plot_weighted_avg_scores(ax, players_data)
        highlight_players(ax, players_data, max_num_matches)
        add_labels(ax, bars, avg_scores)

        ax.set_xlabel("Player")
        ax.set_ylabel("Weighted Average Score")
        ax.set_title("Weighted Average Scores per Player (Winner Highlighted)")
        ax.set_xticklabels(names, rotation=45)
        ax.legend()

        st.pyplot(fig)
