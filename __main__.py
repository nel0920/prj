#!/usr/bin/env python
# -*- coding: utf-8 -*-

from DashAccidents import app

# prevent execution when this module is imported by others
if __name__ == "__main__":
    app.server.run(debug=True, threaded=True, host='0.0.0.0', port=5000)
