#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Import the libraries
import os
from DashAccidents import app

# To prevent execution when this module is imported by others
if __name__ == "__main__":
	port = int(os.environ.get('PORT', 5000))
	app.server.run(debug=True, threaded=True, host ='0.0.0.0', port=port)
