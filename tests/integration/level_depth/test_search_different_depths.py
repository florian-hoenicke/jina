import os

from jina.flow import Flow


def test_index_depth_0_search_depth_1(tmpdir):
    os.environ['JINA_TEST_LEVEL_DEPTH_WORKSPACE'] = str(tmpdir)
    index_data = [
        'I am chunk 0 of doc 1, I am chunk 1 of doc 1, I am chunk 2 of doc 1',
        'I am chunk 0 of doc 2, I am chunk 1 of doc 2',
        'I am chunk 0 of doc 3, I am chunk 1 of doc 3, I am chunk 2 of doc 3, I am chunk 3 of doc 3',
    ]

    index_flow = Flow().load_config('flow-index.yml')
    with index_flow:
        index_flow.index(index_data)

    def validate_granularity_1(resp):
        assert len(resp.docs) == 3
        for doc in resp.docs:
            assert doc.granularity == 0
            assert len(doc.matches) == 3
            assert doc.matches[0].granularity == 0

        assert resp.docs[0].text == ' I am chunk 1 of doc 1,'
        assert (
                resp.docs[0].matches[0].text
                == 'I am chunk 0 of doc 1, I am chunk 1 of doc 1, I am chunk 2 of doc 1'
        )

        assert resp.docs[1].text == 'I am chunk 0 of doc 2,'
        assert (
                resp.docs[1].matches[0].text
                == 'I am chunk 0 of doc 2, I am chunk 1 of doc 2'
        )

        assert resp.docs[2].text == ' I am chunk 3 of doc 3'
        assert (
                resp.docs[2].matches[0].text
                == 'I am chunk 0 of doc 3, I am chunk 1 of doc 3, I am chunk 2 of doc 3, I am chunk 3 of doc 3'
        )

    search_data = [
        ' I am chunk 1 of doc 1,',
        'I am chunk 0 of doc 2,',
        ' I am chunk 3 of doc 3',
    ]

    search_flow = Flow().load_config('flow-query.yml')
    with search_flow:
        search_flow.search(
            input_fn=search_data,
            output_fn=validate_granularity_1,
            callback_on_body=True,
        )

    del os.environ['JINA_TEST_LEVEL_DEPTH_WORKSPACE']
