import logging
import tornado.web
import tornado.ioloop

from tornado.options import options
from webssh.handler import IndexHandler, WsockHandler
from webssh.settings import (
    get_app_settings,  get_host_keys_settings, get_policy_setting,
    get_ssl_context, get_server_settings
)


def make_handlers(loop, options):
    host_keys_settings = get_host_keys_settings(options)
    policy = get_policy_setting(options, host_keys_settings)

    handlers = [
        (r'/', IndexHandler, dict(loop=loop, policy=policy,
                                  host_keys_settings=host_keys_settings)),
        (r'/ws', WsockHandler, dict(loop=loop))
    ]
    return handlers


def make_app(handlers, settings):
    return tornado.web.Application(handlers, **settings)


def main():
    options.parse_command_line()
    loop = tornado.ioloop.IOLoop.current()
    app = make_app(make_handlers(loop, options), get_app_settings(options))
    ssl_ctx = get_ssl_context(options)
    server_settings = get_server_settings(options)
    app.listen(options.port, options.address, **server_settings)
    logging.info('Listening on {}:{}'.format(options.address, options.port))
    if ssl_ctx:
        server_settings.update(ssl_options=ssl_ctx)
        app.listen(options.sslPort, options.sslAddress, **server_settings)
        logging.info('Listening on ssl {}:{}'.format(options.sslAddress,
                                                     options.sslPort))
    loop.start()


if __name__ == '__main__':
    main()
