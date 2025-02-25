import {Client as DiscordClient, ClientEvents, Collection, Intents} from "discord.js";
import {Command} from "./command.js";
import {Listener} from "./listener.js";
import {ModuleBase} from "./moduleBase.js";
import {Task} from "./task.js";

export class Client extends DiscordClient {
    private readonly _modules: Collection<string, ModuleBase>
    private readonly _commands: Collection<string, Command>;
    private readonly _moduleListeners: Collection<keyof ClientEvents, Listener[]>;
    private readonly _tasks: Collection<string, Task>;

    constructor() {
        super({
            intents: [
                Intents.FLAGS.GUILDS,
                Intents.FLAGS.GUILD_BANS,
                Intents.FLAGS.GUILD_MEMBERS,
                Intents.FLAGS.GUILD_MESSAGES,
                Intents.FLAGS.GUILD_MESSAGE_REACTIONS
            ]
        });

        this._commands = new Collection<string, Command>();
        this._tasks = new Collection<string, Task>();
        this._modules = new Collection<string, ModuleBase>();
        this._moduleListeners = new Collection<keyof ClientEvents, Listener[]>();
    }

    get modules(): Collection<string, ModuleBase> {
        return this._modules;
    }

    get commands(): Collection<string, Command> {
        return this._commands;
    }

    get moduleListeners(): Collection<keyof ClientEvents, Listener[]> {
        return this._moduleListeners;
    }

    get tasks(): Collection<string, Task> {
        return this._tasks;
    }
}
