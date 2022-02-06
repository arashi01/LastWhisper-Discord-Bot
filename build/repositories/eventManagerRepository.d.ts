import { Filter } from "mongodb";
import { EventManagerConfig } from "../models/eventManager.js";
export declare class EventManagerRepository {
    private static readonly collectionName;
    private collection;
    constructor();
    private validate;
    save(config: EventManagerConfig): Promise<EventManagerConfig>;
    findOne(filter: Filter<EventManagerConfig>): Promise<EventManagerConfig>;
    find(filter: Filter<EventManagerConfig>): Promise<EventManagerConfig[]>;
    bulkSave(configs: EventManagerConfig[]): Promise<void>;
}
