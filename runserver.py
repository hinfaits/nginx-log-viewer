from nginx_log_viewer import app, get_args

def main():
    args = get_args()
    app.run(host=args.host, port=args.port, debug=True, threaded=True)

if __name__ == "__main__":
    main()
