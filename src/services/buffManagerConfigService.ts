import {BuffManagerConfig} from "../models/buffManager";
import {BuffManagerConfigRepository} from "../repositories/buffManagerConfigRepository";
import {Service} from "typedi";

@Service()
export class BuffManagerConfigService {
    constructor(private repo: BuffManagerConfigRepository) {
    }

    public async findOne(id: string): Promise<BuffManagerConfig> {
        return this.repo.findOne({guildId: id});
    }

    public async findOneOrCreate(id: string): Promise<BuffManagerConfig> {
        let result = await this.repo.findOne({guildId: id})
        if (result) return result;

        result = new BuffManagerConfig();
        result.guildId = id;

        return await this.repo.save(result);
    }

    public async update(config: BuffManagerConfig): Promise<BuffManagerConfig> {
        return this.repo.save(config);
    }

    public async getAll(): Promise<BuffManagerConfig[]> {
        return this.repo.find({});
    }
}