"""A Mac window for the onboarding screens.

PyObjC is already how this repository talks to macOS (Vision, AppKit).
WKWebView is the system view, so the six screens are the existing HTML
inside an NSWindow. That is one window, not a browser page, and it does
not run `open index.html`.
"""
from __future__ import annotations

import json
import sys
import threading
from pathlib import Path


def open_mac_window(*, ui_dir: Path, service) -> None:
    """Open File Companion and block until the window closes.

    On anything other than macOS this raises SystemExit. The screens are
    not opened in a browser instead.
    """
    if sys.platform != "darwin":
        raise SystemExit(
            "File Companion opens a Mac window. This computer is not macOS. "
            "On a Mac, run: python3 -m companion")
    from AppKit import (
        NSApplication,
        NSApplicationActivationPolicyRegular,
        NSBackingStoreBuffered,
        NSMakeRect,
        NSObject,
        NSViewHeightSizable,
        NSViewWidthSizable,
        NSWindow,
        NSWindowStyleMaskClosable,
        NSWindowStyleMaskMiniaturizable,
        NSWindowStyleMaskResizable,
        NSWindowStyleMaskTitled,
    )
    from Foundation import NSURL, NSOperationQueue
    from WebKit import WKWebView, WKWebViewConfiguration

    held = {"webview": None}

    class CompanionHandler(NSObject):
        def userContentController_didReceiveScriptMessage_(self, _controller, message):
            body = _plain(message.body())
            if not isinstance(body, dict):
                body = {}
            method = body.get("method")
            ident = body.get("id")
            payload = body.get("payload")
            if not isinstance(payload, dict):
                payload = {}

            def work() -> None:
                result = _dispatch(service, method, payload)
                _reply(held["webview"], ident, result, NSOperationQueue)

            if method == "scan":
                threading.Thread(target=work, daemon=True).start()
            else:
                work()

    class AppDelegate(NSObject):
        def applicationDidFinishLaunching_(self, _notification):
            style = (
                NSWindowStyleMaskTitled
                | NSWindowStyleMaskClosable
                | NSWindowStyleMaskMiniaturizable
                | NSWindowStyleMaskResizable
            )
            window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
                NSMakeRect(0, 0, 1180, 820), style, NSBackingStoreBuffered, False)
            window.setTitle_("File Companion")
            window.setMinSize_((880, 640))
            config = WKWebViewConfiguration.alloc().init()
            handler = CompanionHandler.alloc().init()
            config.userContentController().addScriptMessageHandler_name_(
                handler, "companion")
            content = window.contentView()
            webview = WKWebView.alloc().initWithFrame_configuration_(
                content.bounds(), config)
            webview.setAutoresizingMask_(NSViewWidthSizable | NSViewHeightSizable)
            held["webview"] = webview
            held["handler"] = handler
            held["window"] = window
            content.addSubview_(webview)
            html = (ui_dir / "index.html").read_text(encoding="utf-8")
            base = NSURL.fileURLWithPath_(str(ui_dir))
            webview.loadHTMLString_baseURL_(html, base)
            window.center()
            window.makeKeyAndOrderFront_(None)
            NSApplication.sharedApplication().activateIgnoringOtherApps_(True)

        def applicationShouldTerminateAfterLastWindowClosed_(self, _sender):
            return True

    app = NSApplication.sharedApplication()
    app.setActivationPolicy_(NSApplicationActivationPolicyRegular)
    delegate = AppDelegate.alloc().init()
    held["delegate"] = delegate
    app.setDelegate_(delegate)
    from PyObjCTools import AppHelper
    AppHelper.runEventLoop()


def _dispatch(service, method: object, payload: dict) -> dict:
    if method == "saveAnswers":
        return service.save_answers(payload)
    if method == "scan":
        return service.scan(payload)
    if method == "workspace":
        return service.workspace(payload)
    if method == "removeEmpty":
        snapshot = payload.get("snapshot")
        if not isinstance(snapshot, dict):
            snapshot = {}
        return service.remove_empty(
            str(payload.get("path") or ""),
            str(payload.get("confirm") or ""),
            snapshot,
        )
    return {"ok": False, "error": "Unknown request."}


def _reply(webview, ident, result: dict, operation_queue) -> None:
    script = "window.fileCompanionDone(%s,%s)" % (
        json.dumps(str(ident)), json.dumps(result))

    def deliver() -> None:
        if webview is not None:
            webview.evaluateJavaScript_completionHandler_(script, None)

    operation_queue.mainQueue().addOperationWithBlock_(deliver)


def _plain(value):
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, dict):
        return {str(key): _plain(item) for key, item in value.items()}
    try:
        keys = list(value.keys())
    except Exception:
        keys = None
    if keys is not None:
        return {str(key): _plain(value[key]) for key in keys}
    try:
        return [_plain(item) for item in value]
    except TypeError:
        return str(value)
