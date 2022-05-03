from edits.levels import main_story
import helper

def timed_scores(save_stats):
    scores = save_stats["itf_timed_scores"]

    usr_scores = [-1] * len(scores)
    usr_scores = helper.edit_array_user(main_story.chapters[3:6], usr_scores, 9999, "Into The Future Timed Scores", "score")
    for i in range(len(usr_scores)):
        if usr_scores[i] != -1:
            scores[i] = ([usr_scores[i]] * 48) + ([0] * 3)
    save_stats["itf_timed_scores"] = scores
    
    print("Successfully set timed scores")
    return save_stats

