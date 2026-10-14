import polars as pl

from scripts.dataset.processing.construct_conversation import ConversationBuilder


def test_reconstruct_conversation():
    tweet_lookup = {
        1: {
            "tweet_id": 1,
            "in_response_to_tweet_id": None,
        },
        2: {
            "tweet_id": 2,
            "in_response_to_tweet_id": 1,
        },
        3: {
            "tweet_id": 3,
            "in_response_to_tweet_id": 2,
        },
    }

    conversation = ConversationBuilder.reconstruct_conversation(
        tweet_id=3,
        tweet_lookup=tweet_lookup,
    )
    tweet_ids = []

    for tweet in conversation:
        tweet_ids.append(tweet["tweet_id"])

    assert tweet_ids == [1, 2, 3]


def test_find_root_tweet():
    tweet_lookup = {
        100: {
            "tweet_id": 100,
            "in_response_to_tweet_id": None,
        },
        101: {
            "tweet_id": 101,
            "in_response_to_tweet_id": 100,
        },
        102: {
            "tweet_id": 102,
            "in_response_to_tweet_id": 101,
        },
        103: {
            "tweet_id": 103,
            "in_response_to_tweet_id": 102,
        },
    }

    root_tweet_id = ConversationBuilder.find_root_tweet(
        tweet_id=103,
        tweet_lookup=tweet_lookup,
    )

    assert root_tweet_id == 100


def test_get_conversation_roots():
    tweet_lookup = {
        100: {
            "tweet_id": 100,
            "in_response_to_tweet_id": None,
        },
        101: {
            "tweet_id": 101,
            "in_response_to_tweet_id": 100,
        },
        102: {
            "tweet_id": 102,
            "in_response_to_tweet_id": 101,
        },
        200: {
            "tweet_id": 200,
            "in_response_to_tweet_id": None,
        },
        201: {
            "tweet_id": 201,
            "in_response_to_tweet_id": 200,
        },
    }

    roots = ConversationBuilder.get_conversation_roots(
        tweet_ids=[101, 102, 201],
        tweet_lookup=tweet_lookup,
    )

    assert roots == {100, 200}


def test_build_child_lookup():
    df = pl.DataFrame(
        {
            "tweet_id": [101, 102, 103],
            "in_response_to_tweet_id": [100, 101, 102],
        }
    )

    child_lookup = ConversationBuilder.build_child_lookup(df)

    assert child_lookup == {
        100: 101,
        101: 102,
        102: 103,
    }


def test_reconstruct_forward_conversation():
    tweet_lookup = {
        100: {
            "tweet_id": 100,
            "in_response_to_tweet_id": None,
        },
        101: {
            "tweet_id": 101,
            "in_response_to_tweet_id": 100,
        },
        102: {
            "tweet_id": 102,
            "in_response_to_tweet_id": 101,
        },
        103: {
            "tweet_id": 103,
            "in_response_to_tweet_id": 102,
        },
    }

    child_lookup = {
        100: 101,
        101: 102,
        102: 103,
    }

    conversation = ConversationBuilder.reconstruct_forward_conversation(
        root_tweet_id=100,
        tweet_lookup=tweet_lookup,
        child_lookup=child_lookup,
    )

    assert [tweet["tweet_id"] for tweet in conversation] == [
        100,
        101,
        102,
        103,
    ]


def test_reconstruct_all_conversations():
    tweet_lookup = {
        100: {
            "tweet_id": 100,
            "in_response_to_tweet_id": None,
        },
        101: {
            "tweet_id": 101,
            "in_response_to_tweet_id": 100,
        },
        200: {
            "tweet_id": 200,
            "in_response_to_tweet_id": None,
        },
        201: {
            "tweet_id": 201,
            "in_response_to_tweet_id": 200,
        },
    }

    child_lookup = {
        100: 101,
        200: 201,
    }

    conversations = ConversationBuilder.reconstruct_all_conversations(
        conversation_roots={100, 200},
        tweet_lookup=tweet_lookup,
        child_lookup=child_lookup,
    )

    conversation_ids = [
        [tweet["tweet_id"] for tweet in conversation] for conversation in conversations
    ]

    assert sorted(conversation_ids) == [
        [100, 101],
        [200, 201],
    ]


def test_flatten_conversations() -> None:
    conversations = [
        [
            {
                "tweet_id": 1,
                "author_id": "customer",
                "inbound": True,
                "created_at": "2026-01-01",
                "text": "I need help",
            },
            {
                "tweet_id": 2,
                "author_id": "AppleSupport",
                "inbound": False,
                "created_at": "2026-01-01",
                "text": "How can we help?",
            },
        ]
    ]

    result = ConversationBuilder.flatten_conversations(conversations)

    assert result.height == 2
    assert result["conversation_id"].to_list() == [1, 1]
    assert result["turn_index"].to_list() == [0, 1]
    assert result["tweet_id"].to_list() == [1, 2]
    assert result["text"].to_list() == [
        "I need help",
        "How can we help?",
    ]
