import main


def test_main_runs_grpc_server(monkeypatch):
    called = False

    async def fake_serve() -> None:
        nonlocal called
        called = True

    monkeypatch.setattr(main, "serve", fake_serve)

    main.main()

    assert called is True
