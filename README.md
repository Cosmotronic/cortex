# Cortex

Named for the artificial minds which control stompy awesome steam
powered robots in [Privateer Press](http://privateerpress.com/)'s game
[Warmachine](http://privateerpress.com/warmachine), Cortex is a tool
for rapidly computing attack values and statistics.

I built Cortex as a learning aid, so that as I play Warmachine I can
rapidly evaluate the probable outcomes of an absurd charge compared to
a more conservative sniper stance in terms of damage dealt, and this
purpuse Cortex serves rather well.

Cortex does not at present provide any assistance in movement planning
or board position analysis. These tasks are both complex and require
that Cortex somehow achieve a total knowlege stance over the game
board which nobody can or should consider fair given the "fog of war"
intent of Warmachine's distance measuring rules.

## Usage

Simply download or clone this repository and execute the file
"src/cortex.py", and you drop into the Cortex read/eval/print loop.

```
Implemented Commands:
	 "help"
		 prints a list of all installe commands

     "help <command>"
		 prints usage information for the mentioned command
		 
     "load models <filename>"
		 loads a model descriptor file, being a list of Model compatible
		 JSON objects and enters them into the interpreter's model table.
    
    "alias model <alias> <model name>"
		 creates an alias for a model, hopefully something easier to type
    
    "ls models"
        enumerates the loaded models by name
    
    "ls aliases"
        enumerates the loaded aliases by abbrev -> real name

	"stats <model>"
		prints model statistics as previously loaded from a datafile

	"attack <model> [with ([def|arm|pow|mat|rat|str] [-|+|=]<number>)+ end]
            <model> [with ([def|arm|pow|mat|rat|str] [-|+|=]<number>)+ end]"
        enumerates and evaluates all attack options for one model
        against another, evaluating every weapon the attacking model
        has against the target at range and in charge. Attacking
        warcasters and warjacks will compute the probable outcomes of
        different boosting strategies as well. This command has a
        boatload of options because it provides support for inline
        stat modifiers.
		
    "reset"
        clears out all the state of the repl, essentially restarting
        it without quitting and reloading the program.
    
    "quit" | "exit" | ":q"
        exits the Cortex program.
```

## Data format

## Legal

I cannot and do not and will not provide the datafiles describing the
models, as they are the sole IP of Privateer Press. These legalities I
am very much aware of, and I have taken pains to purge the data files
which I develop and test against from this project's distributable
repository.

However, I do provide a well documented format which such data could
take, and may extend cortex to include a tool to aid in the
compilation of such data.

## In the pipe
 - Model position/movement AI
 - Target selection AI
 - Vision based board analysis
 - Trivial list management/point counting

## License

This code is made available under the terms of the EPL 1.0, and is
held in sole copyright by Reid "arrdem" McKenzie
