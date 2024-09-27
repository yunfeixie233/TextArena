import textarena
import hydra

@hydra.main(version_base=None, config_path="textarena/codenames")
def main(cfg):

    env = textarena.make("codenames", render_mode="llmagents")
    observation = env.reset()
    env.render()
        
    done = False

    while not done:
        if env.current_role == 'spymaster':
            # Spymaster provides a clue

            # Get clue from user
            board_state = env._get_textual_board_state(env.current_role)
            clue_word, clue_number = env.agent.get_clue(cfg.spymaster.prompt.format(board_state=board_state, team='Red' if env.current_team == 0 else 'Blue'))
            action = (clue_word, clue_number)
            observation, reward, done, info = env.step(action)
        elif env.current_role == 'operative':
            # Operative makes a guess

            # Get clue from user
            board_state = env._get_textual_board_state(env.current_role)
            guess_idx = env.agent.guess_word(cfg.operative.prompt.format(board_state=board_state, clue=env.clue[0], number=env.clue[1]))
            action = guess_idx
            observation, reward, done, info = env.step(action)
        
        env.render()
    
    if env.winner == 'assassin':
        print("Operative guessed the assassin! Game over.")
    elif env.winner:
        print(f"Team {env.winner} wins!")
    else:
        print("Game ended without a clear winner.")

if __name__ == "__main__":
    main()