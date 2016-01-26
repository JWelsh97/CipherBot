import yaml


def read_config():
    """
    Reads the YAML config file
    """
    config = {
        'bot': {
            'host': 'affinity.pw',
            'port': 6697,
            'nickname': ['Cipher', 'Cipher_', 'Cipher__'],
            'password': '',
            'enable_ssl': True
        }
    }

    with open('config.yaml', 'r') as f:
        user_config = yaml.load(f)

    for d in config:
        # Load user config dictionaries
        if d in user_config:
            config[d] = user_config[d]
        else:
            user_config[d] = {}

        # Load user config keys
        for key in config[d]:
            if key in user_config[d]:
                config[d][key] = user_config[d][key]

    if not isinstance(config['bot']['nickname'], list):
        config['bot']['nickname'] = [config['bot']['nickname']]

    return config
