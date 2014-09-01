Contributing
============

Bug reports, feature requests, and other contributions are welcome.
If you find a demonstrable problem that is caused by the code of this
library, please:

1. Search for `already reported problems
   <https://github.com/inveniosoftware/dictdiffer/issues>`_.
2. Check if the issue has been fixed or is still reproducible on the
   latest `master` branch.
3. Create an issue with **a test case**.

If you create a feature branch, you can run the tests to ensure everything is
operating correctly:

.. code-block:: console

    $ ./run-tests.sh

    ...

    Name                  Stmts   Miss  Cover   Missing
    ---------------------------------------------------
    dictdiffer/__init__      88      0   100%
    dictdiffer/version        2      0   100%
    ---------------------------------------------------
    TOTAL                    90      0   100%

    ...

    52 passed, 2 skipped in 0.44 seconds
