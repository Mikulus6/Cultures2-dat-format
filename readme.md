# Cultures2 Data Interpreter

## Progress

✅ - solved (derivation algo exists or section is understood to have non-derivable primary data)  
🟡 - partially solved (in progress)  
❌ - unsolved  

| name   | read algo | write algo | comment                                                                  |
|--------|-----------|------------|--------------------------------------------------------------------------|
| `logi` | ✅         | ✅          | empty                                                                    |
| `lgmm` | ✅         | ✅          | empty                                                                    |
| `lsiz` | ✅         | ✅          | map size (derivable from any array size)                                 |
| `lmhe` | ✅         | ✅          | heightmap (primary)                                                      |
| `lmpa` | ✅         | ❌          |                                                                          |
| `lmpb` | ✅         | ❌          |                                                                          |
| `lmlt` | ✅         | ❌          |                                                                          |
| `lmlv` | ✅         | ❌          |                                                                          |
| `lmlp` | ✅         | ✅          | landscape players (primary) (-1 = default) (>=0 = ID), used for stockade |
| `lmco` | ✅         | ❌          | continents (check required)                                              |
| `lmtw` | ✅         | ❌          |                                                                          |
| `lmms` | ✅         | ❌          |                                                                          |
| `lmpr` | ✅         | ❌          |                                                                          |
| `lmwb` | ✅         | ❌          |                                                                          |
| `lmbb` | ✅         | ❌          |                                                                          |
| `lmro` | ✅         | ❌          |                                                                          |
| `lmsb` | ✅         | ❌          |                                                                          |
| `lmao` | ✅         | ❌          |                                                                          |
| `laco` | ✅         | ❌          | continents metadata                                                      |
| `lasw` | ✅         | ❌          | walk sectors (interpretation required!)                                  |
| `lafm` | ✅         | ✅          | fishes (primary)                                                         |
| `lmhf` | ✅         | ✅          | 2d array, always zeros                                                   |
| `emmm` | ✅         | ✅          | empty                                                                    |
| `embr` | ✅         | ❌          | light (check required)                                                   |
| `emm1` | ✅         | ✅          | visibility of overlay (secondary, derivable from `emmi`)                 |
| `emmi` | ✅         | ✅          | roads/houses vertex type (primary, devs never used houses overlay here)  |
| `eapd` | ✅         | ✅          | patterns ids, text (kind of primary)                                     |
| `empa` | ✅         | ✅          | A-triangles (primary)                                                    |
| `empb` | ✅         | ✅          | B-triangles (primary)                                                    |
| `eatd` | ✅         | ✅          | transitions ids divided by 6, text (primary)                             |
| `emt1` | ✅         | ✅          | transitions A, foreground (primary)                                      |
| `emt2` | ✅         | ✅          | transitions B, foreground (primary)                                      |
| `emt3` | ✅         | ✅          | transitions A, background (primary)                                      |
| `emt4` | ✅         | ✅          | transitions B, background (primary)                                      |
| `eald` | ✅         | ✅          | landscapes ids, text (kind of primary)                                   |
| `emla` | ✅         | ✅          | landscapes (primary)                                                     |
| `emvc` | ✅         | ✅          | vertex colors (primary)                                                  |
| `xend` | ✅         | ✅          | empty                                                                    |
| `tend` | ✅         | ✅          | empty                                                                    |

About `emt` sections: Those are primary transitions data, but I think there exists an objectively
correct way to derive them based on `empa`, `empb`, `eapd` and `eatd`. I haven't figured out this algoritm yet.
Consider also the fact that multiple solutions might exist for single instance of this kind of derivation.

## Introduction

The goal of this project is to write algorithms to freely read and modify
`*.dat` files in games from [*Cultures*](https://de.wikipedia.org/wiki/Cultures_(Computerspielreihe))
series whichs engine is based on [*Cultures 2: The Gates of Asgard*](https://en.wikipedia.org/wiki/Cultures_2:_The_Gates_of_Asgard).
Those are, excluding the mentioned game itself: [*Northland*](https://www.mobygames.com/game/8938/northland/),
[*8th Wonder of the World*](https://www.mobygames.com/game/8939/8th-wonder-of-the-world/) and
[*Cultures: Die Saga*](https://www.mobygames.com/game/11159/cultures-die-saga/).
The plan for this project is analogous to [Cultures Map Editor](https://github.com/Mikulus6/Cultures-map-editor).
For more information visit [CulturesNation](https://culturesnation.pl/).

### License

This program and its source code are distributed under [GNU General Public License 3.0](https://www.gnu.org/licenses/gpl-3.0.txt),
which can be found in the [`license.txt`](license.txt) file. *Cultures* itself
is the property of [Funatics Software](https://www.funatics.de/) with all
rights reserved as stated in the game manual, and is not covered by the
aforementioned license.