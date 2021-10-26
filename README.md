Hey Josh,

I've been fiddling around and found a few more things which you might find 
helpful.

### Number types

From what I can see, Alphavantage returns currency in formation to 4 decimal 
places. Storing this as a float is very wasteful. Instead we can multiply by 
10000 and store as an integer (or if we're given the currency as a string we 
cna just lose the `.`). Also note  that you were storing `Volume` as a 
float and that is always an integer. This has required changes to the pandas 
data frame in `alphavantage_ticker_extractor` and the SQL schema in 
`postgresql_ticker_loader`.

### Store dates as dates not strings

You were copying the dataframe index to a column and then converting it to a 
string. This means that the date will have to be converted back to a date 
from that string at some point. Better is to pass `index=True` and 
`index_columne="Date"` so that the index is written straight to the database 
and not copied. (That said, the next bit makes this irrelevant) 

### Separation of Concerns / Dependency Reduction

Your extract layer is responsible for getting the data in whatever format it 
arrives in. Your transfer layer is responsible for taking that data and 
converting it to a pandas data frame. Your load layer is 
responsible for taking that data frame and storing it somewhere. Because the 
contract between your extract layer and your load layer is a pandas data 
frame your load layer has to depend on pandas. But pandas is a data 
transformation library and the load layer has no business doing any 
transformation. There is an outside chance that the load layer might have to 
do some transformation for wherever it is doing the storage, and if that's 
the case it may choose to pull in pandas - but it shouldn't be forced to. 
I've created a class called `Tick` (which I've put in a `Model` package for 
reasons I'll come to later). I've then refactored the transform and load 
layers so that their contract is a list of `Tick` objects. This means that 
the load layer doesn't need pandas, and it also gives us a nice place to 
stick all the sqlalcamy stuff.

### Table names

Your're including the symbol into the table, when you're storing the symbol 
in each row. Having lots of little tables is 
a great way to make a relational database cry - to the point that sqlalcemy 
doesn't even support it (the table name is tied to the class). This also 
means that the load layer doesn't need to know what the symbol name is - as 
it's provided in the data - which is neater.

### SQL Alchemy versions

SQLALchemy is about to move to version 2.0 which will drop its legacy api, 
so you should pass `future=True` to nearly all the calls to make sure that 
you're 2.0 compatible. I've updated the `PostgresqlTickerLoader` object to 
use the new api and to make use of our `Tick` object. When we spoke I said I 
was going to refactor the database code out of the loader, but as SQLAlchemy 
makes this so trivial I don't think its worth it. We'd just be factoring out 
the `Engine` statement in `__init__` to a common base class and I think that 
makes things harder, rather than easier, in this instance.

I also worked out, and I don't think this was deliberate, that your code and 
my code deleted the entire table when loading a new set of ticks. This would 
mean you'd lose all the historical data you'd harvested, and in my new 
version you'd lose all the data from the other ticks. I've flipped to using 
SQLAlchemy ORM scheme management (the call to `create_all` in `load`) which 
deals with all this for us, and means we can keep all our data intact. As a 
follow up we should have a chat about schema versioning - but there's enough 
change in this already :-)

Notice that I've added a `where()` to the `select()` to take into account 
that we have all the `Tick` objects in the same table.

### Configuration

Never, ever, ever, (ever?) store an API key in code. When I forked your repo 
I got an immediate gitguardian alert that there was a potential key in the 
repo. Right now the extract layer has the alphavantage api key baked into 
the URL. I've added this as a configuration time. I've also put in a light 
touch implementation of a configuration manager so that you can see how it 
might work.

In this design, environment variables are gods and if they are set, that's 
the configuration value. If there is no environment variable, then a config 
file will be looked at, if there's nothing in the config file then we fall 
back to a default or throw an error.

I've defined a config item using a python feature called a `dataclass`. 
Dataclasses just have automation which means we have getters and setters for 
all the fields and a neat default initializer. If I didn't use a dataclass 
we'd have to write this:

```python

class ConfigItem:
    def __init__(self, environment_variable, config_file_key, 
                 default_value=None):
        self._environment_variable = environment_variable
        self._config_file_key = config_file_key
        self._default_value = default_value

    @property
    def environment_variable(self):
        return self._environment_variable

    @environment_variable.setter
    def environment_variable(self, value):
        self._environment_variable = value

    @property
    def config_file_key(self):
        return self._config_file_key

    @config_file_key.setter
    def config_file_key(self, value):
        self._config_file_key = value

    @property
    def default_value(self):
        return self._default_value

    @default_value.setter
    def default_value(self, value):
        self._default_value = value
```

So if nothing else you can see that dataclasses help prevent RSI!!!

The `load_config` method uses a technique known as "asking forgiveness not 
permission". As you can see, we plough in and try and open the file provided.
If it doesn't exist then an exception will be thrown, which we can catch and 
barf nicely at the user. This avoids having to check that the file exists 
every time before we load, but also means that we provide a robust 
implementation.

I've used the magic `__getitem__` method here, for a nice bit of config UI. 
This means that we'll be able to get the configuration values from the 
configuration instance using key value lookup (like `config["API_KEY"]`) 
which feels intuitive to me. Another option is to use `__getattr__ ` and 
attempt to make the interface be `config.API_KEY` but this is tricky as we'd 
have to do special things for special characters; as such it makes the code 
more complex for very little gain.

Having done all that I've added a `setup_config` function in `worker.py` 
which just defines the config parameters which the worker needs.