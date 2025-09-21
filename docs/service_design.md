// Domain Entities

export interface User {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface Interest {
  id: string;
  userId: string;
  name: string;
  description?: string;
  category: InterestCategory;
  priority: Priority;
  createdAt: Date;
  updatedAt: Date;
}

export interface Goal {
  id: string;
  userId: string;
  title: string;
  description: string;
  category: GoalCategory;
  status: GoalStatus;
  priority: Priority;
  targetDate?: Date;
  completedAt?: Date;
  createdAt: Date;
  updatedAt: Date;
}

export interface Resume {
  id: string;
  userId: string;
  name: string;
  content: string;
  format: ResumeFormat;
  isDefault: boolean;
  createdAt: Date;
  updatedAt: Date;
}

export interface ActionItem {
  id: string;
  userId: string;
  title: string;
  description?: string;
  status: ActionItemStatus;
  priority: Priority;
  dueDate?: Date;
  completedAt?: Date;
  relatedOpporunityId?: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface Opporunity {
  id: string;
  title: string;
  company: string;
  description: string;
  requirements: string[];
  type: OpporunityType;
  location?: string;
  isRemote: boolean;
  salaryRange?: SalaryRange;
  postedAt: Date;
  expiresAt?: Date;
  status: OpporunityStatus;
  sourceUrl?: string;
}

export interface UserOpporunity {
  id: string;
  userId: string;
  OpporunityId: string;
  applicationStatus: ApplicationStatus;
  appliedAt?: Date;
  notes?: string;
  coverLetterId?: string;
  resumeId?: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface CoverLetter {
  id: string;
  userId: string;
  OpporunityId?: string;
  title: string;
  content: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface IntroEmail {
  id: string;
  userId: string;
  recipient: string;
  subject: string;
  content: string;
  purpose: EmailPurpose;
  OpporunityId?: string;
  sentAt?: Date;
  createdAt: Date;
  updatedAt: Date;
}

// Enums and Value Objects

export enum InterestCategory {
  INDUSTRY = 'INDUSTRY',
  ROLE = 'ROLE',
  TECHNOLOGY = 'TECHNOLOGY',
  SKILL = 'SKILL',
  COMPANY = 'COMPANY'
}

export enum GoalCategory {
  CAREER = 'CAREER',
  SKILL_DEVELOPMENT = 'SKILL_DEVELOPMENT',
  NETWORKING = 'NETWORKING',
  SALARY = 'SALARY',
  EDUCATION = 'EDUCATION'
}

export enum GoalStatus {
  NOT_STARTED = 'NOT_STARTED',
  IN_PROGRESS = 'IN_PROGRESS',
  COMPLETED = 'COMPLETED',
  PAUSED = 'PAUSED',
  CANCELLED = 'CANCELLED'
}

export enum Priority {
  LOW = 'LOW',
  MEDIUM = 'MEDIUM',
  HIGH = 'HIGH'
}

export enum ResumeFormat {
  PDF = 'PDF',
  DOCX = 'DOCX',
  HTML = 'HTML'
}

export enum ActionItemStatus {
  PENDING = 'PENDING',
  IN_PROGRESS = 'IN_PROGRESS',
  COMPLETED = 'COMPLETED',
  CANCELLED = 'CANCELLED'
}

export enum OpporunityType {
  FULL_TIME = 'FULL_TIME',
  PART_TIME = 'PART_TIME',
  CONTRACT = 'CONTRACT',
  FREELANCE = 'FREELANCE',
  INTERNSHIP = 'INTERNSHIP',
  TEMPORARY = 'TEMPORARY'
}

export enum OpporunityStatus {
  ACTIVE = 'ACTIVE',
  EXPIRED = 'EXPIRED',
  FILLED = 'FILLED',
  CANCELLED = 'CANCELLED'
}

export enum ApplicationStatus {
  SAVED = 'SAVED',
  APPLIED = 'APPLIED',
  SCREENING = 'SCREENING',
  INTERVIEWING = 'INTERVIEWING',
  OFFER = 'OFFER',
  REJECTED = 'REJECTED',
  WITHDRAWN = 'WITHDRAWN',
  ACCEPTED = 'ACCEPTED'
}

export enum EmailPurpose {
  NETWORKING = 'NETWORKING',
  FOLLOW_UP = 'FOLLOW_UP',
  INQUIRY = 'INQUIRY',
  INTRODUCTION = 'INTRODUCTION',
  THANK_YOU = 'THANK_YOU'
}

export interface SalaryRange {
  min: number;
  max: number;
  currency: string;
  period: 'HOURLY' | 'DAILY' | 'WEEKLY' | 'MONTHLY' | 'YEARLY';
}

// Domain Service Interfaces

export interface IInterestService {
  getUserInterests(userId: string): Promise<Interest[]>;
  createInterest(userId: string, interest: Omit<Interest, 'id' | 'userId' | 'createdAt' | 'updatedAt'>): Promise<Interest>;
  updateInterest(id: string, updates: Partial<Interest>): Promise<Interest>;
  deleteInterest(id: string): Promise<void>;
  getInterestsByCategory(userId: string, category: InterestCategory): Promise<Interest[]>;
}

export interface IGoalService {
  getUserGoals(userId: string): Promise<Goal[]>;
  createGoal(userId: string, goal: Omit<Goal, 'id' | 'userId' | 'createdAt' | 'updatedAt'>): Promise<Goal>;
  updateGoal(id: string, updates: Partial<Goal>): Promise<Goal>;
  deleteGoal(id: string): Promise<void>;
  getGoalsByStatus(userId: string, status: GoalStatus): Promise<Goal[]>;
  markGoalComplete(id: string): Promise<Goal>;
}

export interface IResumeService {
  getUserResumes(userId: string): Promise<Resume[]>;
  createResume(userId: string, resume: Omit<Resume, 'id' | 'userId' | 'createdAt' | 'updatedAt'>): Promise<Resume>;
  updateResume(id: string, updates: Partial<Resume>): Promise<Resume>;
  deleteResume(id: string): Promise<void>;
  getDefaultResume(userId: string): Promise<Resume | null>;
  setDefaultResume(id: string): Promise<Resume>;
}

export interface IActionItemService {
  getUserActionItems(userId: string): Promise<ActionItem[]>;
  createActionItem(userId: string, actionItem: Omit<ActionItem, 'id' | 'userId' | 'createdAt' | 'updatedAt'>): Promise<ActionItem>;
  updateActionItem(id: string, updates: Partial<ActionItem>): Promise<ActionItem>;
  deleteActionItem(id: string): Promise<void>;
  getActionItemsByStatus(userId: string, status: ActionItemStatus): Promise<ActionItem[]>;
  getOverdueActionItems(userId: string): Promise<ActionItem[]>;
  markActionItemComplete(id: string): Promise<ActionItem>;
}

export interface IOpporunitySearchService {
  searchOpporunitys(criteria: OpporunitySearchCriteria): Promise<Opporunity[]>;
  getOpporunityById(id: string): Promise<Opporunity | null>;
  getOpporunitysByType(type: OpporunityType): Promise<Opporunity[]>;
  getActiveOpporunitys(): Promise<Opporunity[]>;
}

export interface IOpporunityManagementService {
  getUserOpporunitys(userId: string): Promise<UserOpporunity[]>;
  saveOpporunity(userId: string, OpporunityId: string): Promise<UserOpporunity>;
  applyToOpporunity(userId: string, OpporunityId: string, resumeId: string, coverLetterId?: string): Promise<UserOpporunity>;
  updateApplicationStatus(userOpporunityId: string, status: ApplicationStatus): Promise<UserOpporunity>;
  addOpporunityNotes(userOpporunityId: string, notes: string): Promise<UserOpporunity>;
  getOpporunitysByApplicationStatus(userId: string, status: ApplicationStatus): Promise<UserOpporunity[]>;
}

export interface ICoverLetterService {
  getUserCoverLetters(userId: string): Promise<CoverLetter[]>;
  createCoverLetter(userId: string, coverLetter: Omit<CoverLetter, 'id' | 'userId' | 'createdAt' | 'updatedAt'>): Promise<CoverLetter>;
  updateCoverLetter(id: string, updates: Partial<CoverLetter>): Promise<CoverLetter>;
  deleteCoverLetter(id: string): Promise<void>;
  generateCoverLetter(userId: string, OpporunityId: string, resumeId: string): Promise<CoverLetter>;
}

export interface IIntroEmailService {
  getUserIntroEmails(userId: string): Promise<IntroEmail[]>;
  createIntroEmail(userId: string, email: Omit<IntroEmail, 'id' | 'userId' | 'createdAt' | 'updatedAt'>): Promise<IntroEmail>;
  updateIntroEmail(id: string, updates: Partial<IntroEmail>): Promise<IntroEmail>;
  deleteIntroEmail(id: string): Promise<void>;
  generateIntroEmail(userId: string, purpose: EmailPurpose, OpporunityId?: string): Promise<IntroEmail>;
  markEmailAsSent(id: string): Promise<IntroEmail>;
}

export interface OpporunitySearchCriteria {
  keywords?: string;
  location?: string;
  type?: OpporunityType;
  isRemote?: boolean;
  salaryMin?: number;
  salaryMax?: number;
  postedAfter?: Date;
  limit?: number;
  offset?: number;
}