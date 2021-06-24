细粒度实体分类
============================

.. code-block:: python

    import oknlp


    config = {'batch_size': 16, 'device': 'cuda:0'}
    typing = oknlp.typing.get_by_name(name="bert", **config)
    sents = [
        ("3月15日,北方多地正遭遇近10年来强度最大、影响范围最广的沙尘暴。", [30, 33]),
    ]
    results = typing(sents)
    # result == [[('object', 0.26066625118255615), ('event', 0.9411928653717041)]]
