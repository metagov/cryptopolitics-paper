import os
import pandas as pd

from metagov import at2df # Small custom wrapper functions for the Airtable library
from metagov.utils import ast_eval


# Define list of questions and relevant columns lists, in order
QUESTIONS = {
    'Q1': "1. Which statement comes closest to your views?", 
    'Q2': "2. Which blockchain is the best?", 
    'Q3': "3. Which statement comes closest to your views?", 
    'Q4': "4. Which statement comes closest to your views?", 
    'Q5': "5. Which statement comes closest to your views?", 
    'Q6': "6. Which statement comes closest to your views?", 
    'Q7': "7. Which statement comes closest to your views?", 
    'Q8': "8. Which statement comes closest to your views?", 
    'Q9': "9. In order to grow, the crypto ecosystem should:", 
    'Q10': "10. Which statement comes closest to your views?", 
    'Q11': "11. Which statement comes closest to your views?", 
    'Q12': "12. Which statement comes closest to your views?", 
    'Q13': "13. Which statement comes closest to your views?", 
    'Q14': "14. To get more favorable regulation of cryptocurrencies from national governments, the most important thing the crypto community can do is:", 
    'Q15': "15. Which statement comes closest to your views?", 
    'Q16': "16. Who should have decision-making power over a blockchain?",
    'Q17': "17. I'm here for...", 
    'Q18': "18. Do you consider yourself:", 
    'Q19': "19. OPTIONAL: Do you affiliate with any of the following ecosystems or communities?"
}

CHOICES = {} # Load from dataset

COLS_QUESTIONS = list(QUESTIONS.keys())
COLS_RESULTS = ['classification', 'politics', 'economics', 'governance', 'politics_score', 'politics_score_recomputed', 'politics_recomputed']
COLS_AXES = ['politics', 'economics', 'governance']


# Define the canonical order for the factions/classes (for display purposes)
FACTION_ORDERS = {
    'politics': ['Crypto-leftist', 'Crypto-communitarian', 'Crypto-centrist', 'Crypto-libertarian', 'Crypto-anarchocapitalist'],
    'economics': ['Earner', 'Cryptopunk', 'NPC', 'Techtrepreneur', 'Degen'],
    'governance': ['Walchian', 'Zamfirist', 'Noob', 'Gavinist', 'Szabian']
}

def _rename_col(x):
    """Rename question columns to Q{num} to correspond with QUESTIONS keys;
    leave the rest as is"""
    if x[0].isdigit():
        return n2q(int(x.split('.')[0]))
    else:
        return x


def _rename_faction(x):
    """Rename factions from original quiz naming to journal paper naming"""
    renamed = {
        'DAOist': 'Crypto-communitarian', 
        'True neutral': 'Crypto-centrist', 
        'Crypto-ancap': 'Crypto-anarchocapitalist'
    }
    if x in renamed.keys():
        return renamed[x]
    else:
        return x


def q2n(q):
    """Convert column name for question to question number"""
    return int(q[1:])


def n2q(n):
    """Convert question number to column name for question"""
    return f'Q{n}'


def _compute_politics_score(row):
    """Compute crypto-political score according to the rubric in Table 1"""
    
    POLITICS_GRID = {
        'Q6': {
            'Privacy is the most important feature of blockchain and crypto.': 2,
        },
        'Q7': {
            'Government regulation of crypto will almost always do more harm than good.': 1,
            'Government regulation of crypto is critical to protect the public interest in these technologies.': -1
        },
        'Q9': {
            'Build art and community.': -1,
            'Help people around the world earn a living.': -1,
            'Build useful tech that solve real problems for a set of users.': 1,
            'Provide financial instruments for maximum wealth creation.': 1
        },
        'Q11': {
            'Most crypto teams make a fair and reasonable amount of profit.': 1,
            'Crypto teams make too much profit.': -1
        },
        'Q12': {
            'The economic system in crypto is generally fair to most of its participants.': 1,
            'The economic system in crypto unfairly favors powerful interests.': -1
        },
        'Q13': {
            "Most people who want to get ahead in crypto can make it if they're willing to work hard.": 1,
            "In crypto, hard work and determination are no guarantee of success for most people.": -1
        },
        'Q14': {
            "Keep on doing what we’re doing, legal or not.": 1
        },
        'Q15': {
            'Crypto does not have a gender problem.': 1
        },
        'Q18': {
            'Liberal or left-wing': -1,
            'Conservative or right-wing': 1
        }
    }
    
    scores = [POLITICS_GRID.get(q, {}).get(row[q], 0) for q in COLS_QUESTIONS[:-1]]
    score = sum(scores)
    return score


def _get_politics_type(score):
    """Compute crypto-political type based on score"""
    
    if score <= -3:
        return 'Crypto-leftist'
    if score < 0:
        return 'Crypto-communitarian'
    if score == 0:
        return 'Crypto-centrist'
    if score < 5:
        return 'Crypto-libertarian'
    if score >= 5:
        return 'Crypto-anarchocapitalist'
    else:
        raise


def load_data(overwrite=False):
    """Load the data from Govbase. Assumes Govbase data is already clean."""
    
    datapath = 'data/cryptopolitics_survey_data.csv'
    if  (not os.path.isfile(datapath)) or overwrite:
        at = at2df.get_airtable()
        df = at2df.get_table_as_df(at, 'Cryptopolitical Typology Quiz')

        # Rename question columns for easier accessing/visualization throughout
        df.rename(columns=_rename_col, inplace=True)
        df.to_csv(datapath, columns=[*QUESTIONS.keys(), 'classification', 'politics_score', 'politics', 'economics', 'governance', 'Submitted At'])
        
    else:
        df = pd.read_csv(datapath, index_col=0)
        df['Q19'] = df['Q19'].apply(ast_eval)

    df['politics'] = df['politics'].apply(_rename_faction)
    df['politics_score_recomputed'] = df.apply(_compute_politics_score, axis=1)
    df['politics_recomputed'] = df['politics_score_recomputed'].apply(_get_politics_type)
    
    # Split data into question responses and faction results DataFrames
    df_questions = df[COLS_QUESTIONS]
    df_results = df[COLS_RESULTS]

    # Get unique answer choices for each question
    for question in COLS_QUESTIONS[:-1]:
        choices = list(df_questions[question].unique())
        CHOICES[question] = choices       
        
    return {'responses': df_questions, 'results': df_results}


if __name__ == "__main__":
    from datetime import datetime

    # Test database loading
    t0 = datetime.now()
    load_data(overwrite=True)
    t1 = datetime.now()
    print(f"Time to load from Airtable: {t1-t0}")
    load_data()
    t2 = datetime.now()
    print(f"Time to load from file:     {t2-t1}")
