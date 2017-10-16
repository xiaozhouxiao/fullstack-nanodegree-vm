#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2, bleach


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    """db = psycopg2.connect("dbname=tournament")
    c = db.cursor()
    c.execute("psql \c tournament")
    return db"""


def deleteMatches():
    """Remove all the match records from the database."""
    db = psycopg2.connect("dbname=tournament")
    c = db.cursor()
    deleteMatchQuery = """
        UPDATE scores
        SET wins = 0, matches = 0
        WHERE id != -1;
        """
    c.execute(deleteMatchQuery)
    db.commit()
    db.close()


def deletePlayers():
    """Remove all the player records from the database."""
    db = psycopg2.connect("dbname=tournament")
    c = db.cursor()
    c.execute("DELETE FROM players;");
    db.commit()
    db.close()


def countPlayers():
    """Returns the number of players currently registered."""
    db = psycopg2.connect("dbname=tournament")
    c = db.cursor()
    c.execute("select count(*) from players;")
    count = c.fetchall()
    db.close()
    return count[0][0]


def registerPlayer(playerName):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """
    db = psycopg2.connect("dbname=tournament")
    c = db.cursor()
    c.execute("INSERT INTO players (name) VALUES (%s);", (bleach.clean(playerName),))
    c.execute("SELECT id FROM players WHERE name = %s;", (playerName,))
    playerID = c.fetchall()
    c.execute("INSERT INTO scores (id, wins, matches) VALUES (%s, 0, 0);", (playerID[0][0],))
    db.commit()
    db.close()


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    db = psycopg2.connect("dbname=tournament")
    c = db.cursor()
    standingQuery = """
        SELECT players.id, players.name, scores.wins, scores.matches
        FROM players LEFT JOIN scores
        ON players.id = scores.id
        ORDER BY scores.wins;
        """
    c.execute(standingQuery)
    standings = c.fetchall()
    db.commit()
    db.close()
    return standings


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    db = psycopg2.connect("dbname=tournament")
    c = db.cursor()
    reportQuery = """
        UPDATE scores SET matches = matches + 1 WHERE id = %s;
        UPDATE scores SET matches = matches + 1 WHERE id = %s;
        UPDATE scores SET wins = wins + 1 WHERE id = %s;
        """
    c.execute(reportQuery, (winner, loser, winner))
    db.commit()
    db.close()


def swissPairings():
    """Returns a list of pairs of players for the next round of a match.

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    standings = playerStandings()
    nPlayers = countPlayers()
    parings = []
    for match in range(nPlayers/2):
        parings.append([standings[match * 2][0], standings[match * 2][1],
                          standings[match * 2 + 1][0], standings[match * 2 + 1][1]])
    return parings




