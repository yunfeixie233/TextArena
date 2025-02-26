# SimpleNegotiation Environment Documentation

## Overview
**SimpleNegotiation** is a two-player strategic trading game where players exchange resources with different personal valuations to maximize their overall inventory value. Unlike the multi-player Negotiation environment, this simplified version focuses on direct one-to-one trading with a streamlined offer and response system. Players can communicate freely while making trade offers or responding to opponents' proposals. The goal is to execute trades that increase the total value of your resource portfolio based on your personal resource valuations.

## Action Space

- **Format:** Actions are strings that can include conversational text and one of the following commands:
  - **Trade Offer:** `[Offer: Resources -> Resources]` - Propose a trade of specific resources
  - **Accept Offer:** `[Accept]` - Accept a pending trade offer
  - **Deny Offer:** `[Deny]` - Reject a pending trade offer (also happens by default)

- **Examples:**
  - Make a trade offer: `I'm interested in your Wood. [Offer: 3 Sheep, 2 Ore -> 5 Wood]`
  - Accept a pending offer: `That seems fair, I'll take the deal. [Accept]`
  - Deny an offer: `I don't think that works for me. [Deny]`

- **Notes:** Players can include conversational text before and after their action commands. Only one offer can be active at a time, and only the player who received an offer can accept or deny it.

## Observation Space

**Reset Observations**
On reset, each player receives a prompt containing their resource information and personal valuations. For example:

```plaintext
You are Player 0 in the Negotiation Game.
You have some resources, and your task is to trade such that the total value of your resources increases.
The resources and associated values you currently have are:
	+ [Wheat]    Qty: 12   Value: 6
	+ [Wood]     Qty: 18   Value: 8
	+ [Sheep]    Qty: 8    Value: 17
	+ [Brick]    Qty: 10   Value: 23
	+ [Ore]      Qty: 7    Value: 35
At each turn, you can talk to your opponent or make a trade offer.
Use the following special tokens for actions:
  - [Offer]: To make a trade offer.
    Format: [Offer: Offered Resources -> Requested Resources]
    Example: [Offer: 3 Sheep, 2 Ore -> 5 Brick, 2 Sheep]
  - [Accept]: To accept an incoming offer.
  - [Deny]: To deny an incoming offer (default).
You can include additional text before and/or after these tokens.
The game lasts for 10 turns in total.
```

**Step Observations**
During gameplay, players receive various observations based on actions taken. For example:

```plaintext
[Player 0] I notice you have quite a lot of Wheat. I could use some for my development. [Offer: 2 Brick, 1 Ore -> 5 Wheat]
[GAME] Player 0 made the following offer to Player 1: Offered items: 2 Brick, 1 Ore -> Requested items: 5 Wheat
[Player 1] That's a bit steep for me, but I'm willing to trade some Wheat. Let me counter with a better offer. [Offer: 3 Wheat -> 1 Brick, 1 Ore]
[GAME] Player 1 made the following offer to Player 0: Offered items: 3 Wheat -> Requested items: 1 Brick, 1 Ore
[Player 0] That works for me. I accept your offer. [Accept]
[GAME] Player 0 accepted the trade offer from Player 1.
```

## Gameplay

- **Players:** 2 players
- **Initial Setup:** Each player starts with random amounts of five different resources (Wheat, Wood, Sheep, Brick, Ore)
- **Resource Valuation:** Each player has personal valuations for each resource that vary slightly from base market values
- **Turns:** Players take turns communicating and making/responding to trade offers
- **Objective:** Maximize the increase in your total resource portfolio value compared to your starting value
- **Maximum Turns:** Configurable, default is 10 turns

## Key Rules

1. **Resource Management:**
   - Each player begins with random amounts (5-25) of five different resources
   - Each player has unique personal valuations for each resource (±20% variation from base values)
   - Players can only trade resources they possess in sufficient quantities

2. **Trading System:**
   - **Making Offers:** Specify resources to give and receive in the format `[Offer: X, Y -> A, B]`
   - **Accepting Offers:** The recipient of an offer can accept it by using `[Accept]`
   - **Denying Offers:** The recipient can explicitly deny using `[Deny]` or implicitly by making a counter-offer
   - **Trade Execution:** When a trade is accepted, resources are exchanged immediately if both parties have sufficient quantities

3. **Offer Lifecycle:**
   - Only one trade offer can be active at a time
   - A new offer replaces any previous pending offer
   - After an offer is accepted or denied, a new offer must be made to continue trading

4. **Valid Moves:**
   - Trade offers must specify valid resource types and quantities
   - Players must have sufficient resources to fulfill their side of the trade
   - Only the player to whom an offer was made can accept or deny it

5. **Winning Conditions:**
   - **Win:** The player with the greatest increase in total inventory value from their starting position
   - **Draw:** Both players achieve the same increase in inventory value
   - **Loss:** Having a smaller increase in inventory value than your opponent

6. **Game Termination:**
   - The game concludes after a predetermined number of turns (default: 10)
   - Final scores are calculated based on each player's personal valuations of their current resources compared to their initial resources

## Rewards

| Outcome     | Reward for Winner | Reward for Loser |
|-------------|:-----------------:|:----------------:|
| **Win**     | `+1`              | `-1`             |
| **Draw**    | `0`               | `0`              |
| **Invalid** | `-1`              | `0`              |

## Parameters

- `max_turns` (`int`, default: `10`):
  - **Description:** Sets the maximum number of turns before the game ends
  - **Impact:** Longer games allow for more complex negotiation strategies and multiple trades

## Variants

| Env-id                        | max_turns |
|-------------------------------|:---------:|
| `SimpleNegotiation-v0`        | `10`      |
| `SimpleNegotiation-v0-short`  | `6`       |
| `SimpleNegotiation-v0-long`   | `30`      |



### Contact
If you have questions or face issues with this specific environment, please reach out directly to Guertlerlo@cfar.a-star.edu.sg