from services.setup.repair_action import RepairAction
from services.setup.repairs.ollama_install_repair import (
    OLLAMA_WINDOWS_DOWNLOAD_URL,
    OllamaInstallRepair,
)


def test_ollama_install_repair_opens_official_download() -> None:
    opened_urls = []

    repair = OllamaInstallRepair(
        browser_opener=(
            lambda url: (
                opened_urls.append(url)
                or True
            )
        )
    )

    result = repair(
        {
            "capability_id": (
                "artificial-intelligence"
            ),
        }
    )

    assert opened_urls == [
        OLLAMA_WINDOWS_DOWNLOAD_URL
    ]
    assert result.user_action_required is True
    assert (
        result.action
        == RepairAction.INSTALL_AI_PROVIDER
    )
    assert (
        result.details["download_url"]
        == OLLAMA_WINDOWS_DOWNLOAD_URL
    )


def test_ollama_install_repair_reports_browser_false() -> None:
    repair = OllamaInstallRepair(
        browser_opener=lambda url: False
    )

    result = repair({})

    assert result.failed is True
    assert (
        result.details["reason"]
        == "browser-open-returned-false"
    )


def test_ollama_install_repair_reports_browser_exception() -> None:
    def failing_opener(url):
        raise RuntimeError(
            "browser unavailable"
        )

    repair = OllamaInstallRepair(
        browser_opener=failing_opener
    )

    result = repair({})

    assert result.failed is True
    assert (
        result.details["reason"]
        == "browser-open-failed"
    )
    assert (
        result.details["error"]
        == "browser unavailable"
    )
