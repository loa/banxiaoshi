# 半小时

[![Build Status](https://travis-ci.org/loa/banxiaoshi.png?branch=master)](https://travis-ci.org/loa/banxiaoshi)

## Add users

Add users by adding them into users.yaml. Password is your regular skritter password but encrypted with rsa.

    echo -n "your_skritter_password" | openssl rsautl -encrypt -pubin -inkey encrypt/public_rsa.pem | base64
