/**
 * Typed stand-ins for the two connector clients that App Builder generates once
 * OneDrive for Business and Office 365 Users are bound (generated/services/*).
 *
 * MOCK-UP PHASE ONLY. These exist so brief-store.ts compiles before connectors exist;
 * every method throws "Connector not bound". In MOCK_MODE the store never calls them.
 *
 * Build phase: bind the connectors, repoint the two imports in brief-store.ts to
 * ../../generated/services/OneDriveforBusinessService and ../../generated/services/Office365UsersService,
 * then delete this file.
 */

export interface IOperationResult<T> {
  success: boolean;
  data?: T;
  error?: unknown;
}

/** Subset of the generated OneDrive BlobMetadata model used by brief-store. */
export interface BlobMetadata {
  Id?: string;
  Name?: string;
  Path?: string;
  LastModified?: string;
  Size?: number;
  ETag?: string;
  IsFolder?: boolean;
}

/** Subset of the generated Graph user model used by brief-store. */
export interface GraphUser_V1 {
  id?: string;
  displayName?: string;
  givenName?: string;
  jobTitle?: string;
  mail?: string;
  userPrincipalName?: string;
}

const notBound = (op: string): never => {
  throw new Error(`Connector not bound: ${op}. Bind OneDrive for Business and Office 365 Users, then repoint brief-store.ts to generated/services.`);
};

export class OneDriveforBusinessService {
  static async GetFileContentByPath(_path: string, _inferContentType?: boolean): Promise<IOperationResult<string>> { return notBound("OneDrive.GetFileContentByPath"); }
  static async GetFileContent(_id: string, _inferContentType?: boolean): Promise<IOperationResult<string>> { return notBound("OneDrive.GetFileContent"); }
  static async GetFileMetadataByPath(_path: string): Promise<IOperationResult<BlobMetadata>> { return notBound("OneDrive.GetFileMetadataByPath"); }
  static async CreateFile(_folderPath: string, _name: string, _body: string): Promise<IOperationResult<BlobMetadata>> { return notBound("OneDrive.CreateFile"); }
  static async UpdateFile(_id: string, _body: string): Promise<IOperationResult<BlobMetadata>> { return notBound("OneDrive.UpdateFile"); }
}

export class Office365UsersService {
  static async MyProfile_V2(_$select?: string): Promise<IOperationResult<GraphUser_V1>> { return notBound("Office365Users.MyProfile_V2"); }
  static async DirectReports_V2(_id: string, _$select?: string, _$top?: number): Promise<IOperationResult<{ value: GraphUser_V1[] }>> { return notBound("Office365Users.DirectReports_V2"); }
}
