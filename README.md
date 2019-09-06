# parsnip

parsnip is a minimal command line tool used to quickly compare commits
between two branches. Commits that share a hash between both branches will be labeled green. Commits that share a message but not a hash will be labeled yellow. All other commits are labeled red. 


![Example](https://i.imgur.com/uwV5I9C.png)

parsnip accepts one or two arguments. If provided with one argument, it will use the current branch to compare the provided one against. If provided with two arguments, it will compare the two branches against each other. 

## Getting Started

### Prerequisites

```
Python 3.6 or higher
```

### Installing

```
git clone https://github.com/Samwest5/parsnip.git
```

### Running

```
python ./parsnip.py args
```

## Authors

* **Sam Westigard**

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
