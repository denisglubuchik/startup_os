from main import main


def test_main_prints_service_name(capsys):
    main()

    captured = capsys.readouterr()
    assert captured.out == "Hello from experimentation-service!\n"
