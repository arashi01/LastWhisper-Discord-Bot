"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const dayjs_1 = __importDefault(require("dayjs"));
const discord_js_1 = require("discord.js");
const ManagerUtils_1 = __importDefault(require("../schema/ManagerUtils"));
const Module_1 = require("../classes/Module");
const Listener_1 = __importDefault(require("../classes/Listener"));
async function getConfig(guildId) {
    return await ManagerUtils_1.default.findOne({ _id: guildId }) ?? await ManagerUtils_1.default.create({ _id: guildId });
}
async function getLoggingChannel(client, guildId) {
    const config = await getConfig(guildId);
    if (!config.loggingChannel)
        return null;
    const loggingChannel = await client.channels.fetch(config.loggingChannel);
    return loggingChannel && typeof loggingChannel === typeof discord_js_1.TextChannel ? loggingChannel : null;
}
async function onMemberLeave(member) {
    const loggingChannel = await getLoggingChannel(member.client, member.guild.id);
    if (!loggingChannel)
        return;
    const kickedData = (await member.guild.fetchAuditLogs({
        limit: 1,
        type: "MEMBER_KICK"
    })).entries.first();
    const embed = new discord_js_1.MessageEmbed()
        .setColor("RANDOM")
        .addFields({ name: "Joined On:", value: (0, dayjs_1.default)(member.joinedAt).format("HH:mm:ss DD/MM/YYYY") }, { name: "Nickname was:", value: member.nickname ?? "None" }, { name: "Roles:", value: member.roles.cache.map(role => role.toString()).join(" ") })
        .setThumbnail(member.user.displayAvatarURL());
    if (kickedData && kickedData.target.id === member.id) {
        embed.setTitle("User Kicked!")
            .setDescription(`User **${member.displayName}** was kicked by **${(await member.guild.members.fetch(kickedData.executor.id)).displayName}** from the server.`);
    }
    else {
        embed.setTitle("User Left!")
            .setDescription(`User **${member.displayName}** has left this discord server`);
    }
    await loggingChannel.send({ embeds: [embed] });
}
async function onMemberBanned(ban) {
    const loggingChannel = await getLoggingChannel(ban.client, ban.guild.id);
    if (!loggingChannel)
        return;
    const banLogs = (await ban.guild.fetchAuditLogs({ limit: 1, type: "MEMBER_BAN_ADD" })).entries.first();
    if (banLogs) {
        const executor = banLogs.executor;
        const target = banLogs.target;
        const embed = new discord_js_1.MessageEmbed()
            .setTitle("Member Banned!")
            .setColor("RANDOM");
        if (target) {
            embed
                .setDescription(`User **${target.tag}** was banned by ${executor ? (await ban.guild.members.fetch(executor.id)).displayName : "Someone who was not part of the server somehow... what how?? "}!`)
                .setThumbnail(target.displayAvatarURL());
        }
        else {
            embed.setDescription("Somehow a user was banned but we cannot find out who it was!");
        }
        await loggingChannel.send({ embeds: [embed] });
    }
    else {
        await loggingChannel.send("A ban somehow occurred but no logs about it could be found!");
    }
}
class ManagerUtils extends Module_1.Module {
    constructor() {
        super("ManagerUtils");
        this.listeners = [
            new Listener_1.default(`${this.name}#OnGuildBanAdd`, "guildBanAdd", onMemberBanned),
            new Listener_1.default(`${this.name}#OnGuildMemberRemove`, "guildMemberRemove", async (member) => {
                console.log("Guild member was removed.");
                if (member.partial)
                    await member.fetch();
                await onMemberLeave(member);
            })
        ];
    }
}
exports.default = new ManagerUtils();
