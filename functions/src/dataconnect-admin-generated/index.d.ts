import { ConnectorConfig, DataConnect, OperationOptions, ExecuteOperationResponse } from 'firebase-admin/data-connect';

export const connectorConfig: ConnectorConfig;

export type TimestampString = string;
export type UUIDString = string;
export type Int64String = string;
export type DateString = string;


export interface ChampionshipConfig_Key {
  id: UUIDString;
  __typename?: 'ChampionshipConfig_Key';
}

export interface CreateConfigData {
  championshipConfig_insert: ChampionshipConfig_Key;
}

export interface CreateConfigVariables {
  eventId: UUIDString;
}

export interface CreateEventData {
  event_insert: Event_Key;
}

export interface CreateScoreData {
  score_insert: Score_Key;
}

export interface CreateScoreVariables {
  regId: UUIDString;
  eventId: UUIDString;
  points: number;
}

export interface CreateUserDataData {
  user_insert: User_Key;
}

export interface DeleteConfigData {
  championshipConfig_delete?: ChampionshipConfig_Key | null;
}

export interface DeleteConfigVariables {
  id: UUIDString;
}

export interface DeleteEventData {
  event_delete?: Event_Key | null;
}

export interface DeleteEventVariables {
  id: UUIDString;
}

export interface DeleteRegistrationData {
  registration_delete?: Registration_Key | null;
}

export interface DeleteRegistrationVariables {
  id: UUIDString;
}

export interface DeleteScoreData {
  score_delete?: Score_Key | null;
}

export interface DeleteScoreVariables {
  id: UUIDString;
}

export interface DeleteUserDataData {
  user_delete?: User_Key | null;
}

export interface DeleteUserDataVariables {
  id: UUIDString;
}

export interface Event_Key {
  id: UUIDString;
  __typename?: 'Event_Key';
}

export interface GetConfigData {
  championshipConfig?: {
    weightageMultiplier: number;
    isDay2Component: boolean;
  };
}

export interface GetConfigVariables {
  id: UUIDString;
}

export interface GetEventData {
  event?: {
    name: string;
    category: string;
  };
}

export interface GetEventVariables {
  id: UUIDString;
}

export interface GetRegistrationData {
  registration?: {
    status: string;
    event: {
      name: string;
    };
  };
}

export interface GetRegistrationVariables {
  id: UUIDString;
}

export interface GetScoreData {
  score?: {
    points: number;
    roundName: string;
  };
}

export interface GetScoreVariables {
  id: UUIDString;
}

export interface GetUserData {
  user?: {
    email: string;
    role: string;
    collegeName: string;
  };
}

export interface GetUserVariables {
  id: UUIDString;
}

export interface ListConfigsData {
  championshipConfigs: ({
    event: {
      name: string;
    };
    weightageMultiplier: number;
  })[];
}

export interface ListEventsData {
  events: ({
    name: string;
    day: number;
  })[];
}

export interface ListRegistrationsData {
  registrations: ({
    user: {
      email: string;
    };
    event: {
      name: string;
    };
    status: string;
  })[];
}

export interface ListScoresData {
  scores: ({
    points: number;
    roundName: string;
    event: {
      name: string;
    };
  })[];
}

export interface ListUsersData {
  users: ({
    email: string;
    collegeName: string;
  })[];
}

export interface RegisterForEventData {
  registration_insert: Registration_Key;
}

export interface RegisterForEventVariables {
  userId: UUIDString;
  eventId: UUIDString;
}

export interface Registration_Key {
  id: UUIDString;
  __typename?: 'Registration_Key';
}

export interface Score_Key {
  id: UUIDString;
  __typename?: 'Score_Key';
}

export interface UpdateConfigData {
  championshipConfig_update?: ChampionshipConfig_Key | null;
}

export interface UpdateConfigVariables {
  id: UUIDString;
  multiplier: number;
}

export interface UpdateEventData {
  event_update?: Event_Key | null;
}

export interface UpdateEventVariables {
  id: UUIDString;
  desc?: string | null;
}

export interface UpdateRegistrationData {
  registration_update?: Registration_Key | null;
}

export interface UpdateRegistrationVariables {
  id: UUIDString;
  status: string;
}

export interface UpdateScoreData {
  score_update?: Score_Key | null;
}

export interface UpdateScoreVariables {
  id: UUIDString;
  points: number;
}

export interface UpdateUserDataData {
  user_update?: User_Key | null;
}

export interface UpdateUserDataVariables {
  id: UUIDString;
  phone?: string | null;
}

export interface User_Key {
  id: UUIDString;
  __typename?: 'User_Key';
}

/** Generated Node Admin SDK operation action function for the 'CreateUserData' Mutation. Allow users to execute without passing in DataConnect. */
export function createUserData(dc: DataConnect, options?: OperationOptions): Promise<ExecuteOperationResponse<CreateUserDataData>>;
/** Generated Node Admin SDK operation action function for the 'CreateUserData' Mutation. Allow users to pass in custom DataConnect instances. */
export function createUserData(options?: OperationOptions): Promise<ExecuteOperationResponse<CreateUserDataData>>;

/** Generated Node Admin SDK operation action function for the 'UpdateUserData' Mutation. Allow users to execute without passing in DataConnect. */
export function updateUserData(dc: DataConnect, vars: UpdateUserDataVariables, options?: OperationOptions): Promise<ExecuteOperationResponse<UpdateUserDataData>>;
/** Generated Node Admin SDK operation action function for the 'UpdateUserData' Mutation. Allow users to pass in custom DataConnect instances. */
export function updateUserData(vars: UpdateUserDataVariables, options?: OperationOptions): Promise<ExecuteOperationResponse<UpdateUserDataData>>;

/** Generated Node Admin SDK operation action function for the 'DeleteUserData' Mutation. Allow users to execute without passing in DataConnect. */
export function deleteUserData(dc: DataConnect, vars: DeleteUserDataVariables, options?: OperationOptions): Promise<ExecuteOperationResponse<DeleteUserDataData>>;
/** Generated Node Admin SDK operation action function for the 'DeleteUserData' Mutation. Allow users to pass in custom DataConnect instances. */
export function deleteUserData(vars: DeleteUserDataVariables, options?: OperationOptions): Promise<ExecuteOperationResponse<DeleteUserDataData>>;

/** Generated Node Admin SDK operation action function for the 'GetUser' Query. Allow users to execute without passing in DataConnect. */
export function getUser(dc: DataConnect, vars: GetUserVariables, options?: OperationOptions): Promise<ExecuteOperationResponse<GetUserData>>;
/** Generated Node Admin SDK operation action function for the 'GetUser' Query. Allow users to pass in custom DataConnect instances. */
export function getUser(vars: GetUserVariables, options?: OperationOptions): Promise<ExecuteOperationResponse<GetUserData>>;

/** Generated Node Admin SDK operation action function for the 'ListUsers' Query. Allow users to execute without passing in DataConnect. */
export function listUsers(dc: DataConnect, options?: OperationOptions): Promise<ExecuteOperationResponse<ListUsersData>>;
/** Generated Node Admin SDK operation action function for the 'ListUsers' Query. Allow users to pass in custom DataConnect instances. */
export function listUsers(options?: OperationOptions): Promise<ExecuteOperationResponse<ListUsersData>>;

/** Generated Node Admin SDK operation action function for the 'CreateEvent' Mutation. Allow users to execute without passing in DataConnect. */
export function createEvent(dc: DataConnect, options?: OperationOptions): Promise<ExecuteOperationResponse<CreateEventData>>;
/** Generated Node Admin SDK operation action function for the 'CreateEvent' Mutation. Allow users to pass in custom DataConnect instances. */
export function createEvent(options?: OperationOptions): Promise<ExecuteOperationResponse<CreateEventData>>;

/** Generated Node Admin SDK operation action function for the 'UpdateEvent' Mutation. Allow users to execute without passing in DataConnect. */
export function updateEvent(dc: DataConnect, vars: UpdateEventVariables, options?: OperationOptions): Promise<ExecuteOperationResponse<UpdateEventData>>;
/** Generated Node Admin SDK operation action function for the 'UpdateEvent' Mutation. Allow users to pass in custom DataConnect instances. */
export function updateEvent(vars: UpdateEventVariables, options?: OperationOptions): Promise<ExecuteOperationResponse<UpdateEventData>>;

/** Generated Node Admin SDK operation action function for the 'DeleteEvent' Mutation. Allow users to execute without passing in DataConnect. */
export function deleteEvent(dc: DataConnect, vars: DeleteEventVariables, options?: OperationOptions): Promise<ExecuteOperationResponse<DeleteEventData>>;
/** Generated Node Admin SDK operation action function for the 'DeleteEvent' Mutation. Allow users to pass in custom DataConnect instances. */
export function deleteEvent(vars: DeleteEventVariables, options?: OperationOptions): Promise<ExecuteOperationResponse<DeleteEventData>>;

/** Generated Node Admin SDK operation action function for the 'GetEvent' Query. Allow users to execute without passing in DataConnect. */
export function getEvent(dc: DataConnect, vars: GetEventVariables, options?: OperationOptions): Promise<ExecuteOperationResponse<GetEventData>>;
/** Generated Node Admin SDK operation action function for the 'GetEvent' Query. Allow users to pass in custom DataConnect instances. */
export function getEvent(vars: GetEventVariables, options?: OperationOptions): Promise<ExecuteOperationResponse<GetEventData>>;

/** Generated Node Admin SDK operation action function for the 'ListEvents' Query. Allow users to execute without passing in DataConnect. */
export function listEvents(dc: DataConnect, options?: OperationOptions): Promise<ExecuteOperationResponse<ListEventsData>>;
/** Generated Node Admin SDK operation action function for the 'ListEvents' Query. Allow users to pass in custom DataConnect instances. */
export function listEvents(options?: OperationOptions): Promise<ExecuteOperationResponse<ListEventsData>>;

/** Generated Node Admin SDK operation action function for the 'RegisterForEvent' Mutation. Allow users to execute without passing in DataConnect. */
export function registerForEvent(dc: DataConnect, vars: RegisterForEventVariables, options?: OperationOptions): Promise<ExecuteOperationResponse<RegisterForEventData>>;
/** Generated Node Admin SDK operation action function for the 'RegisterForEvent' Mutation. Allow users to pass in custom DataConnect instances. */
export function registerForEvent(vars: RegisterForEventVariables, options?: OperationOptions): Promise<ExecuteOperationResponse<RegisterForEventData>>;

/** Generated Node Admin SDK operation action function for the 'UpdateRegistration' Mutation. Allow users to execute without passing in DataConnect. */
export function updateRegistration(dc: DataConnect, vars: UpdateRegistrationVariables, options?: OperationOptions): Promise<ExecuteOperationResponse<UpdateRegistrationData>>;
/** Generated Node Admin SDK operation action function for the 'UpdateRegistration' Mutation. Allow users to pass in custom DataConnect instances. */
export function updateRegistration(vars: UpdateRegistrationVariables, options?: OperationOptions): Promise<ExecuteOperationResponse<UpdateRegistrationData>>;

/** Generated Node Admin SDK operation action function for the 'DeleteRegistration' Mutation. Allow users to execute without passing in DataConnect. */
export function deleteRegistration(dc: DataConnect, vars: DeleteRegistrationVariables, options?: OperationOptions): Promise<ExecuteOperationResponse<DeleteRegistrationData>>;
/** Generated Node Admin SDK operation action function for the 'DeleteRegistration' Mutation. Allow users to pass in custom DataConnect instances. */
export function deleteRegistration(vars: DeleteRegistrationVariables, options?: OperationOptions): Promise<ExecuteOperationResponse<DeleteRegistrationData>>;

/** Generated Node Admin SDK operation action function for the 'GetRegistration' Query. Allow users to execute without passing in DataConnect. */
export function getRegistration(dc: DataConnect, vars: GetRegistrationVariables, options?: OperationOptions): Promise<ExecuteOperationResponse<GetRegistrationData>>;
/** Generated Node Admin SDK operation action function for the 'GetRegistration' Query. Allow users to pass in custom DataConnect instances. */
export function getRegistration(vars: GetRegistrationVariables, options?: OperationOptions): Promise<ExecuteOperationResponse<GetRegistrationData>>;

/** Generated Node Admin SDK operation action function for the 'ListRegistrations' Query. Allow users to execute without passing in DataConnect. */
export function listRegistrations(dc: DataConnect, options?: OperationOptions): Promise<ExecuteOperationResponse<ListRegistrationsData>>;
/** Generated Node Admin SDK operation action function for the 'ListRegistrations' Query. Allow users to pass in custom DataConnect instances. */
export function listRegistrations(options?: OperationOptions): Promise<ExecuteOperationResponse<ListRegistrationsData>>;

/** Generated Node Admin SDK operation action function for the 'CreateScore' Mutation. Allow users to execute without passing in DataConnect. */
export function createScore(dc: DataConnect, vars: CreateScoreVariables, options?: OperationOptions): Promise<ExecuteOperationResponse<CreateScoreData>>;
/** Generated Node Admin SDK operation action function for the 'CreateScore' Mutation. Allow users to pass in custom DataConnect instances. */
export function createScore(vars: CreateScoreVariables, options?: OperationOptions): Promise<ExecuteOperationResponse<CreateScoreData>>;

/** Generated Node Admin SDK operation action function for the 'UpdateScore' Mutation. Allow users to execute without passing in DataConnect. */
export function updateScore(dc: DataConnect, vars: UpdateScoreVariables, options?: OperationOptions): Promise<ExecuteOperationResponse<UpdateScoreData>>;
/** Generated Node Admin SDK operation action function for the 'UpdateScore' Mutation. Allow users to pass in custom DataConnect instances. */
export function updateScore(vars: UpdateScoreVariables, options?: OperationOptions): Promise<ExecuteOperationResponse<UpdateScoreData>>;

/** Generated Node Admin SDK operation action function for the 'DeleteScore' Mutation. Allow users to execute without passing in DataConnect. */
export function deleteScore(dc: DataConnect, vars: DeleteScoreVariables, options?: OperationOptions): Promise<ExecuteOperationResponse<DeleteScoreData>>;
/** Generated Node Admin SDK operation action function for the 'DeleteScore' Mutation. Allow users to pass in custom DataConnect instances. */
export function deleteScore(vars: DeleteScoreVariables, options?: OperationOptions): Promise<ExecuteOperationResponse<DeleteScoreData>>;

/** Generated Node Admin SDK operation action function for the 'GetScore' Query. Allow users to execute without passing in DataConnect. */
export function getScore(dc: DataConnect, vars: GetScoreVariables, options?: OperationOptions): Promise<ExecuteOperationResponse<GetScoreData>>;
/** Generated Node Admin SDK operation action function for the 'GetScore' Query. Allow users to pass in custom DataConnect instances. */
export function getScore(vars: GetScoreVariables, options?: OperationOptions): Promise<ExecuteOperationResponse<GetScoreData>>;

/** Generated Node Admin SDK operation action function for the 'ListScores' Query. Allow users to execute without passing in DataConnect. */
export function listScores(dc: DataConnect, options?: OperationOptions): Promise<ExecuteOperationResponse<ListScoresData>>;
/** Generated Node Admin SDK operation action function for the 'ListScores' Query. Allow users to pass in custom DataConnect instances. */
export function listScores(options?: OperationOptions): Promise<ExecuteOperationResponse<ListScoresData>>;

/** Generated Node Admin SDK operation action function for the 'CreateConfig' Mutation. Allow users to execute without passing in DataConnect. */
export function createConfig(dc: DataConnect, vars: CreateConfigVariables, options?: OperationOptions): Promise<ExecuteOperationResponse<CreateConfigData>>;
/** Generated Node Admin SDK operation action function for the 'CreateConfig' Mutation. Allow users to pass in custom DataConnect instances. */
export function createConfig(vars: CreateConfigVariables, options?: OperationOptions): Promise<ExecuteOperationResponse<CreateConfigData>>;

/** Generated Node Admin SDK operation action function for the 'UpdateConfig' Mutation. Allow users to execute without passing in DataConnect. */
export function updateConfig(dc: DataConnect, vars: UpdateConfigVariables, options?: OperationOptions): Promise<ExecuteOperationResponse<UpdateConfigData>>;
/** Generated Node Admin SDK operation action function for the 'UpdateConfig' Mutation. Allow users to pass in custom DataConnect instances. */
export function updateConfig(vars: UpdateConfigVariables, options?: OperationOptions): Promise<ExecuteOperationResponse<UpdateConfigData>>;

/** Generated Node Admin SDK operation action function for the 'DeleteConfig' Mutation. Allow users to execute without passing in DataConnect. */
export function deleteConfig(dc: DataConnect, vars: DeleteConfigVariables, options?: OperationOptions): Promise<ExecuteOperationResponse<DeleteConfigData>>;
/** Generated Node Admin SDK operation action function for the 'DeleteConfig' Mutation. Allow users to pass in custom DataConnect instances. */
export function deleteConfig(vars: DeleteConfigVariables, options?: OperationOptions): Promise<ExecuteOperationResponse<DeleteConfigData>>;

/** Generated Node Admin SDK operation action function for the 'GetConfig' Query. Allow users to execute without passing in DataConnect. */
export function getConfig(dc: DataConnect, vars: GetConfigVariables, options?: OperationOptions): Promise<ExecuteOperationResponse<GetConfigData>>;
/** Generated Node Admin SDK operation action function for the 'GetConfig' Query. Allow users to pass in custom DataConnect instances. */
export function getConfig(vars: GetConfigVariables, options?: OperationOptions): Promise<ExecuteOperationResponse<GetConfigData>>;

/** Generated Node Admin SDK operation action function for the 'ListConfigs' Query. Allow users to execute without passing in DataConnect. */
export function listConfigs(dc: DataConnect, options?: OperationOptions): Promise<ExecuteOperationResponse<ListConfigsData>>;
/** Generated Node Admin SDK operation action function for the 'ListConfigs' Query. Allow users to pass in custom DataConnect instances. */
export function listConfigs(options?: OperationOptions): Promise<ExecuteOperationResponse<ListConfigsData>>;

